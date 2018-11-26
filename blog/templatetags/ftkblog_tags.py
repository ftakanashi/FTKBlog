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
            return u''
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

@register.tag(name='load_theme_change')
def load_theme_change(parser, token):
    try:
        flag = Dict.objects.get(key='themeChange').value
    except Exception,e:
        flag = False
    if flag == '1':
        s = '''
        <div class="fix-tool-btn" id="refreshTheme" title="刷新主题">
                <a href="javascript:void(0);"><i class="fa fa-refresh"></i></a>
        </div>
        '''
    else:
        s = ''

    return template.base.TextNode(s)


@register.tag(name='load_bgm')
def load_bgm(parser, token):
    try:
        flag = Dict.objects.get(key='bgmSwitch').value
    except Exception,e:
        flag = False

    if flag == '1':
        s = '''
        <h5 class="footer-title">BGM</h5>
        <iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width=330 height=110 src="//music.163.com/outchain/player?type=0&id=2389989722&auto=0&height=90"></iframe>
        '''
    else:
        s = ''

    return template.base.TextNode(s)