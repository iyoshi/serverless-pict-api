import unittest
from unittest import mock

import jwt

from src import post_images
from tests.testing.dynamodb_testing_util import DynamoDbTestingUtil

dynamodb_local = DynamoDbTestingUtil.create_dynamodb_local_resource()


class TestPostImages(unittest.TestCase):

    def setUp(self):
        dynamodb_local.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'photo_id',
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
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            },
        )

    def tearDown(self):
        DynamoDbTestingUtil.delete_table('photos')

    @mock.patch('boto3.resource')
    def test_handler_ok(self, mock_resource):
        table = dynamodb_local.Table('photos')
        table.put_item(Item={
            'photo_id': 'photo_id'
        })

        mock_resource.return_value = dynamodb_local

        access_token = jwt.encode({'sub': 'user_id'}, 'secret')
        event = {
            'body': "{\"type\": \"img/jpeg\", \"size\": 1}",
            'headers': {
                'Authorization': access_token
            }
        }
        actual = post_images.handler(event, None)
        self.assertEqual(actual['statusCode'], 200)
