import json
import logging
import os

import boto3
from botocore.client import ClientError

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

    photo_id = path_params['image_id']

    dynamodb = boto3.resource('dynamodb',
                              region_name=os.getenv('AWS_DEFAULT_REGION'))
    table = dynamodb.Table(os.getenv('PHOTOS_TABLE_NAME', 'photos'))
    try:
        result = table.get_item(Key={'photo_id': photo_id})

        if 'Item' not in result:
            return {
                'statusCode': 404,
                'body': 'Resource not found',
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }

        table.delete_item(Key={'photo_id': photo_id})

    except ClientError as err:
        logger.error(err.response['Error']['Code'])

        return {
            'statusCode': 500,
            'body': err.response['Error']['Code'],
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    logger.info('photo_id = %s is successfully deleted.', photo_id)

    return {
        'statusCode': 200,
        'body': json.dumps({'photo_id': photo_id}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
