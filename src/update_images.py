import json
import logging
from pynamodb.exceptions import UpdateError, GetError

from src.decimalencoder import DecimalEncoder
from src.models.images import Images

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def validate_request_body(body):
    return body.keys() >= {'image_id', 'status'}


def handler(event, context):
    """
    TBD.

    :param event: TBD
    :param context: TBD
    :return: TBD
    """

    body = json.loads(event['body'])
    if not validate_request_body(body):
        logger.error("Validation Failed")

        return {
            'statusCode': 400,
            'body': 'Required params is invalid',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': "*"
            }
        }

    image_id = body['image_id']
    status = body['status']

    image: Images = None
    try:
        Images(image_id).update({'status': {'value': status, 'action': 'PUT'}})
        image = Images.get(image_id)

    except (UpdateError, GetError) as err:
        return {
            'statusCode': 500,
            'body': err.msg,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    try:
        response_body = {
            'image_id': image.image_id,
            'status': image.status,
            'type': image.type,
            'size': image.size,
            'created_at': image.created_at,
            'version': image.version
        }

        return {
            'statusCode': 200,
            'body': json.dumps(response_body, cls=DecimalEncoder),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    except Exception as err:
        logger.error('type: %s', type(err))

        return {
            'statusCode': 500,
            'body': 'Unexpected error occurred',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
