# -*- coding:utf-8 -*-

'''
some custom model fields class
'''
from IPy import IP

# from django.core.exceptions import ValidationError
from django.db.models import CharField

class IPyIPSegmentField(CharField):

    description = 'a class to save an ip segment implemented by IPy'

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 32
        super(CharField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return IP(value)

    # def to_python(self, value):
    #     print value
    #     if value is None or isinstance(value, IP):
    #         return value
    #
    #     try:
    #         print value
    #         return IP(value)
    #     except Exception,e:
    #         raise ValidationError('Invalid input for a IPy.IP instance: %s' % str(e))
    #
    # def get_prep_value(self, value):
    #     print 'get_prep_value called'
    #     print value
    #     return '11' + str(value) + '11'
    #
    # def get_db_prep_value(self, value, connection, prepared=False):
    #     return '22' + str(value) + '22'



