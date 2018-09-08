import unittest
from unittest import mock

from src.models.images import Images, UserIdIndex
from src.daos.imagesdao import ImagesDao

images_local = Images()
images_local.Meta.host = 'http://localhost:8000'

IMAGE_ID = 'image_id'
USER_ID = 'user_id'
TYPE = 'type'
SIZE = 0
STATUS = 'status'

class TestImagesDao(unittest.TestCase):

    def setUp(self):
        images_local.create_table(True, read_capacity_units=1, write_capacity_units=1)

    def tearDown(self):
        images_local.delete_table()

    @mock.patch('src.models.images')
    def test_create_ok(self, mock_resource):
        images_local.image_id = IMAGE_ID
        images_local.user_id = USER_ID
        images_local.type = TYPE
        images_local.size = SIZE
        images_local.status = STATUS

        mock_resource.return_value = images_local

        dao = ImagesDao()
        actual = dao.create(images_local)

        self.assertEqual(actual.image_id, IMAGE_ID)
        self.assertIsNotNone(actual.created_at)
        self.assertIsNotNone(actual.updated_at)
        self.assertEqual(actual.version, 0)

    @mock.patch('src.models.images')
    def test_find(self, mock_resource):
        images_local.image_id = IMAGE_ID
        images_local.user_id = USER_ID
        images_local.type = TYPE
        images_local.size = SIZE
        images_local.status = STATUS

        mock_resource.return_value = images_local

        dao = ImagesDao()
        dao.create(images_local)

        actual = dao.find(IMAGE_ID)
        self.assertEqual(actual.image_id, IMAGE_ID)
        self.assertEqual(actual.user_id, USER_ID)

        actual = dao.find('not_found')
        self.assertIsNone(actual)

    @mock.patch('src.models.images')
    def test_find_all_with_user_id(self, mock_resource):
        images_local.image_id = IMAGE_ID
        images_local.user_id = USER_ID
        images_local.type = TYPE
        images_local.size = SIZE
        images_local.status = STATUS

        mock_resource.return_value = images_local

        dao = ImagesDao()
        dao.create(images_local)

        actual = dao.find_all_with_user_id(USER_ID)
        self.assertEqual(len(list(actual)), 1)

        actual = dao.find_all_with_user_id('not_found')
        self.assertEqual(len(list(actual)), 0)

    @mock.patch('src.models.images')
    def test_update(self, mock_resource):
        images_local.image_id = IMAGE_ID
        images_local.user_id = USER_ID
        images_local.type = TYPE
        images_local.size = SIZE
        images_local.status = STATUS

        mock_resource.return_value = images_local

        dao = ImagesDao()
        expected = dao.create(images_local)

        actions = [Images.status.set('updated')]
        actual = dao.update(expected, actions)
        self.assertEqual(actual.status, 'updated')

    @mock.patch('src.models.images')
    def test_delete(self, mock_resource):
        images_local.image_id = IMAGE_ID
        images_local.user_id = USER_ID
        images_local.type = TYPE
        images_local.size = SIZE
        images_local.status = STATUS

        mock_resource.return_value = images_local

        dao = ImagesDao()
        expected = dao.create(images_local)

        dao.delete(expected)

        actual = dao.find(IMAGE_ID)
        self.assertIsNone(actual)
