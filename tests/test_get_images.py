import unittest
import json
from unittest import mock

import jwt

from src import get_images
from tests.testing.dynamodb_testing_util import DynamoDbTestingUtil

dynamodb_local = DynamoDbTestingUtil.create_dynamodb_local_resource()


class TestGetImages(unittest.TestCase):

    def setUp(self):
        dynamodb_local.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'photo_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                }
            ],
            TableName='photos',
            KeySchema=[
                {
                    'AttributeName': 'photo_id',
                    'KeyType': 'HASH'
                },
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'user_id-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 1,
                        'WriteCapacityUnits': 1
                    }
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )

    def tearDown(self):
        DynamoDbTestingUtil.delete_table('photos')

    @mock.patch('boto3.resource')
    def test_handler_ok(self, mock_resource):
        table = dynamodb_local.Table('photos')
        table.put_item(Item={
            'photo_id': 'photo_id',
            'user_id': 'user_id',
            'status': 'uploaded'
        })

        mock_resource.return_value = dynamodb_local

        access_token = jwt.encode({'sub': 'user_id'}, 'secret')
        event = {
            'headers': {
                'Authorization': access_token
            }
        }

        actual = get_images.handler(event, None)
        self.assertEqual(actual['statusCode'], 200)
        self.assertEqual(actual['body'], json.dumps(
            {'photos': [
                {
                    'photo_id': 'photo_id',
                    'user_id': 'user_id',
                    'status': 'uploaded'
                }
            ]}
        ))
