import unittest
from unittest import mock

import jwt

from src import get_images
from src.models.images import Images

images_local = Images()
images_local.Meta.host = 'http://localhost:8000'


class TestGetImages(unittest.TestCase):

    def setUp(self):
        images_local.create_table(True, read_capacity_units=1, write_capacity_units=1)

    def tearDown(self):
        images_local.delete_table()

    @mock.patch('src.models.images')
    def test_handler_ok(self, mock_resource):
        images_local.image_id = 'image_id'
        images_local.user_id = 'user_id'
        images_local.type = 'type'
        images_local.size = 0
        images_local.status = 'status'
        images_local.save()

        mock_resource.return_value = images_local

        access_token = jwt.encode({'sub': 'user_id'}, 'secret')
        event = dict(headers={'Authorization': access_token})

        actual = get_images.handler(event, None)
        self.assertEqual(actual['statusCode'], 200)
