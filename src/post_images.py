import datetime
import json
import logging
import uuid

from pynamodb.exceptions import PutError, GetError
import jwt

from src.models.images import Images

# TODO: use logger class
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):

    body = json.loads(event['body'])
    credentials = jwt.decode(event['headers']['Authorization'], verify=False)
    user_id = credentials['sub']

    image_id = str(uuid.uuid4())

    image = Images(image_id)
    image.user_id = user_id
    image.status = 'waiting'
    image.type = body['type']
    image.size = body['size']
    image.created_at = int(datetime.datetime.utcnow().timestamp())

    entity: Images = None
    try:
        image.save()
        entity = image.get(image_id)

    except (PutError, GetError) as err:

        return {
            'statusCode': 500,
            'body': err.msg,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    response_body = {
        'image_id': entity.image_id,
        'user_id': entity.user_id,
        'status': entity.status,
        'type': entity.type,
        'size': entity.size,
        'created_at': entity.created_at,
        'version': entity.version
    }

    return {
        'statusCode': 200,
        'body': json.dumps(response_body),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
