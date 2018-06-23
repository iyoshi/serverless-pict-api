import os
from datetime import datetime

from pynamodb.attributes import NumberAttribute
from pynamodb.attributes import UnicodeAttribute
from pynamodb.constants import DEFAULT_REGION
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.models import Model


class UserIdIndex(GlobalSecondaryIndex):
    """
    Model class for global secondary index of Images
    """

    class Meta:
        index_name = 'UserID-index'
        projection = AllProjection()
        read_capacity_units = 1
        write_capacity_units = 1

    user_id = UnicodeAttribute(hash_key=True, attr_name='UserID')


class Images(Model):
    """
    Model class of Images table
    """

    class Meta:
        table_name = os.getenv('IMAGES_TABLE_NAME', 'Images')
        region = os.getenv('AWS_DEFAULT_REGION', DEFAULT_REGION)
        read_capacity_units = 1
        write_capacity_units = 1

    image_id = UnicodeAttribute(hash_key=True, attr_name='ImageID')
    user_id = UnicodeAttribute(attr_name='UserID', null=False)
    user_id_index = UserIdIndex()
    status = UnicodeAttribute(attr_name='Status')
    type = UnicodeAttribute(attr_name='Type')
    size = NumberAttribute(attr_name='Size')
    created_at = NumberAttribute(attr_name='CreatedAt',
                                 default=datetime.utcnow().timestamp())
    updated_at = NumberAttribute(attr_name='UpdatedAt', null=True)
    version = NumberAttribute(attr_name='Version', default=0)
