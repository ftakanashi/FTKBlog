# -*- coding:utf-8 -*-

from django import template

from blog.models import Dict

register = template.Library()

class DictItemNode(template.Node):
    def __init__(self, key):
        self.key = key

    def render(self, context):
        try:
            item = Dict.objects.get(key=self.key)
        except Dict.DoesNotExist,e:
            return u'文本丢失啦'
        return item.value

@register.tag(name='dictitem')
def get_dict_item(parser,token):
    try:
        tag,key = token.split_contents()
    except ValueError,e:
        raise template.TemplateSyntaxError('%s tag takes one argument' % token.split_contents()[0])
    if not key[0] == key[-1] or key[0] not in ('"','\''):
        raise template.TemplateSyntaxError('%s should be quoted' % key)

    return DictItemNode(key=key[1:-1])