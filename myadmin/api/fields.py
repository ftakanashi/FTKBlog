# -*- coding:utf-8 -*-

import json

from rest_framework.serializers import RelatedField

class PostWithUuidField(RelatedField):

    def to_representation(self, value):
        return json.dumps({'title': value.title, 'uuid': str(value.post_uuid)})