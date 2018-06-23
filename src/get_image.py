import json
import logging

from pynamodb.exceptions import DoesNotExist, GetError

from src.decimalencoder import DecimalEncoder
from src.models.images import Images

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    TBD.

    :param event: TBD
    :param context: TBD
    :return: TBD
    """

    path_params = event['pathParameters']

    if 'image_id' not in path_params:
        logger.error("Validation Failed")

        return {
            'statusCode': 400,
            'body': 'Required params is invalid',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    image_id = path_params['image_id']
    image: Images = None
    try:
        image = Images.get(hash_key=image_id, consistent_read=True)

    except DoesNotExist as err:

        return {
            'statusCode': 404,
            'body': err.msg,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    except GetError as err:

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

        return {
            'statusCode': 500,
            'body': 'Unexpected error occurred',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
