# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

from ftkuser.models import AccessControl

class AccessControlMiddleware(MiddlewareMixin):

    def process_request(self, request):
        source_ip = request.META.get('REMOTE_ADDR')
        auth_flag = True
        for ac in AccessControl.objects.filter(control_type='1',domain='root'):
            if source_ip in ac.source_ip:
                auth_flag = False
                break
        if not auth_flag:
            ctx = {'error_msg': '抱歉，你已经被拉黑了，无法访问本站。如果是误报请联系管理员',
                   'error_title': '拉黑提示'}
            return render(request, 'error.html', ctx)

        # try:
        #     AccessControl.objects.get(control_type='1', source_ip=source_ip,domain='root')
        # except AccessControl.DoesNotExist,e:
        #     return
        # else:
        #     ctx = {'error_msg': '抱歉，你已经被拉黑了，无法访问本站。如果是误报请联系管理员',
        #            'error_title': '拉黑提示'}
        #     return render(request, 'error.html', ctx)