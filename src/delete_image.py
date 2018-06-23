import json
import logging

from pynamodb.exceptions import DoesNotExist, DeleteError
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
    try:
        image = Images.get(hash_key=image_id)
        image.delete()

    except DoesNotExist as err:
        return {
            'statusCode': 404,
            'body': err.msg,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    except DeleteError as err:
        return {
            'statusCode': 500,
            'body': err.msg,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    logger.info('photo_id = %s is successfully deleted.', image_id)

    return {
        'statusCode': 200,
        'body': json.dumps({'image_id': image_id}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
