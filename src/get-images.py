import json
import logging
import os

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.client import ClientError

from src.decimalencoder import DecimalEncoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_DEFAULT_REGION'))
table = dynamodb.Table(os.getenv('PHOTOS_TABLE_NAME'))


def handler(event, context):
    """
    TBD.

    :param event: TBD
    :param context: TBD
    :return: TBD
    """

    try:
        result = table.scan(FilterExpression=Attr('status').eq('uploaded'))

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

    try:
        items = {
            'photos': result['Items']
        }

        return {
            'statusCode': 200,
            'body': json.dumps(items, cls=DecimalEncoder),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    except Exception as err:
        logger.error('type: {}'.format(type(err)))
        logger.error(err)

        return {
            'statusCode': 500,
            'body': 'Unexpected error occurred',
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
