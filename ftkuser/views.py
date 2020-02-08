# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, reverse, redirect
from django.views import View
from django.http import HttpResponseForbidden, JsonResponse, QueryDict
from django.contrib.auth import logout, authenticate, login

from ratelimit.decorators import ratelimit

from .models import Slogan, AccessControl

import logging
import random
import re
import traceback

logger = logging.getLogger('django')

# Create your views here.
class UserLogout(View):
    def post(self, request):
        ctx = {
            'error_title': '错误的请求方法',
            'error_msg': 'POST方法不适用于登出用户'
        }
        return HttpResponseForbidden(render(request, 'error.html', ctx))

    def get(self, request):
        logout(request)
        return redirect(reverse('index'))


class UserLogin(View):
    TOLARENCE = 10

    def _randomGetSlogan(self):
        return random.choice(Slogan.objects.all())

    @ratelimit(key='ip', rate='1/1s')
    def get(self, request):
        try:
            referer = request.META.get('HTTP_REFERER')
            m = re.match('https?\://(?:.+?)(/.+)$', referer)
            newPostUrl = reverse('new_post')
            editPostUrl = reverse('post.manage')
            url = m.group(1)

            if url == newPostUrl \
                or \
            url.startswith(editPostUrl) and len(editPostUrl) < len(url):
                return JsonResponse({'msg': '登录状态已经失效，请尝试重新登录后刷新页面'}, status=500)
        except Exception,e:
            pass

        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

        ctx = {}

        auth_flag = False
        src_ip = request.META.get('REMOTE_ADDR')
        for ac in AccessControl.objects.filter(control_type='0', domain='root'):
            if src_ip in ac.source_ip:
                auth_flag = True
                break

        if not auth_flag:
            return render(request, 'error.html', {'error_msg': '只有授权的人才能尝试登录ヾ(◍°∇°◍)ﾉﾞ', 'refresh_btn': True})

        next = request.GET.get('next', reverse('index'))

        # 如果已经登录了
        if request.user.is_active:
            return redirect(next)

        # slogan彩蛋
        if request.GET.get('changeslogan') == 'true':
            slogan = self._randomGetSlogan()
            ctx['content'] = slogan.content
            ctx['author'] = slogan.author
            return JsonResponse(ctx)

        ctx['slogan'] = self._randomGetSlogan()
        return render(request, 'ftkuser/login.html', ctx)

    @ratelimit(key='ip', rate='3/m')
    def post(self, request):

        if getattr(request, 'limited', False):
            if getattr(request, 'limited_usage_count', -1) > self.TOLARENCE:
                ac = AccessControl(control_type='1', source_ip=request.META.get('REMOTE_ADDR'))
                ac.save()
                return JsonResponse({'msg': '不好意思，你已经被拉黑。如果是误报，请联系管理员'})
            return JsonResponse({'msg': '您的登录尝试过于频繁，请稍后再试...'}, status=500)

        ctx = {}
        username = request.POST.get('u')
        password = request.POST.get('p')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            try:
                login(request, user)
            except Exception, e:
                logger.error(traceback.format_exc(e))
                return JsonResponse({'msg': '登录失败'}, status=500)
            else:
                if user.is_staff:
                    return JsonResponse({'next': reverse('my_admin_index')})
                    # return JsonResponse({'next': reverse('admin:index')})
                else:
                    return JsonResponse({'next': reverse('index')})
        else:
            return JsonResponse({'msg': '用户名或密码错误'}, status=500)

    def put(self, request):

        PUT = QueryDict(request.body)

        if PUT.get('act') == 'save':    # 编辑文章自动保存重定向到登录View的请求
            return JsonResponse({'msg': '登录信息已失效，请重新登录'}, status=403)

        return JsonResponse({'msg': '错误的请求方法'}, status=405)
