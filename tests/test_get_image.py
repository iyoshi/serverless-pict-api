import json
import unittest
from unittest import mock

from src import get_image
from src.models.images import Images

images_local = Images()
images_local.Meta.host = 'http://localhost:8000'


class TestGetImage(unittest.TestCase):

    def setUp(self):
        images_local.create_table(True, read_capacity_units=1, write_capacity_units=1)

    def tearDown(self):
        images_local.delete_table()

    @mock.patch("src.models.images")
    def test_handler_ok(self, mock_resource):
        images_local.image_id = "image_id"
        images_local.user_id = "user_id"
        images_local.type = "type"
        images_local.size = 0
        images_local.status = "status"
        images_local.save()

        mock_resource.return_value = images_local

        event = dict(pathParameters={"image_id": "image_id"})

        actual = get_image.handler(event, None)
        self.assertEqual(actual["statusCode"], 200)
        actual_body = json.loads(actual["body"])
        self.assertEqual(actual_body["image_id"], "image_id")
        self.assertEqual(actual_body["type"], "type")
        self.assertEqual(actual_body["size"], 0)
        self.assertEqual(actual_body["status"], "status")
        self.assertIsNotNone(actual_body['created_at'])
        self.assertEqual(actual_body["version"], 0)

    @mock.patch("src.models.images")
    def test_handler_fail_ifRequiredParamsIsInvalid(self, mock_resource):
        mock_resource.return_value = images_local
        event = dict(pathParameters={})

        actual = get_image.handler(event, None)
        self.assertEqual(actual["statusCode"], 400)

    @mock.patch('src.models.images')
    def test_handler_fail_ifPhotoResourceNotFound(self, mock_resource):
        images_local.image_id = "image_id"
        images_local.user_id = "user_id"
        images_local.type = "type"
        images_local.size = 0
        images_local.status = "status"
        images_local.save()

        mock_resource.return_value = images_local

        event = dict(pathParameters={"image_id": "not_found"})
        actual = get_image.handler(event, None)
        self.assertEqual(actual["statusCode"], 404)
