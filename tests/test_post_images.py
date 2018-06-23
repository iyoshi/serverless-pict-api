import json
import unittest
from unittest import mock

import jwt

from src import post_images
from src.models.images import Images

images_local = Images()
images_local.Meta.host = 'http://localhost:8000'


class TestPostImages(unittest.TestCase):

    def setUp(self):
        images_local.create_table(True, read_capacity_units=1, write_capacity_units=1)

    def tearDown(self):
        images_local.delete_table()

    @mock.patch('src.models.images')
    def test_handler_ok(self, mock_resource):
        mock_resource.return_value = images_local

        access_token = jwt.encode({'sub': 'user_id'}, 'secret')
        event = dict(
            body=json.dumps({"type": "img/jpeg", "size": 1}),
            headers={'Authorization': access_token}
        )
        actual = post_images.handler(event, None)
        self.assertEqual(actual['statusCode'], 200)
        actual_body = json.loads(actual['body'])
        self.assertIsNotNone(actual_body['image_id'])
        self.assertEqual(actual_body['status'], 'waiting')
        self.assertEqual(actual_body['type'], 'img/jpeg')
        self.assertEqual(actual_body['size'], 1)
