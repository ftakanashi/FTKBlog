# -*- coding:utf-8 -*-

from blog.models import Dict

def site_switch_control(request):
    if request.method == 'GET':
        _extra_ctx = {'site_switch__' + i.key:i.value == '1' for i in Dict.objects.filter(category='site_switch')}
        return _extra_ctx

def site_global_dictval(request):
    if request.method == 'GET':
        _extra_ctx = {'site_globalv__' + i.key:i.value for i in Dict.objects.filter(category='site_global_value')}
        return _extra_ctx

