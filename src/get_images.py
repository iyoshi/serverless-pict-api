import json
import logging

import jwt
from pynamodb.exceptions import QueryError

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

    access_token = event['headers']['Authorization']
    credentials = jwt.decode(access_token, verify=False)
    user_id = credentials['sub']

    try:
        images: [Images] = Images.user_id_index.query(
            user_id,
            limit=100,
            consistent_read=False,
            filter_condition=(Images.status == 'uploaded'))

    except QueryError as err:

        return {
            'statusCode': 500,
            'body': err.msg,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    try:
        items = [
            {
                'image_id': e.image_id,
                'status': e.status,
                'type': e.type,
                'size': e.size,
                'created_at': e.created_at,
                'version': e.version
            } for e in images]
        response_body = {
            'images': items
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
        logger.error(err)

        return {
            'statusCode': 500,
            'body': 'Unexpected error occurred',
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
