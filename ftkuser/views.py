# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, reverse, redirect
from django.views import View
from django.http import HttpResponseForbidden,JsonResponse
from django.contrib.auth import logout, authenticate, login

from ratelimit.decorators import ratelimit

# Create your views here.
class UserLogout(View):

    def post(self,request):
        ctx = {
            'error_title': '错误的请求方法',
            'error_msg': 'POST方法不适用于登出用户'
        }
        return HttpResponseForbidden(render(request,'error.html',ctx))

    def get(self,request):
        logout(request)
        return redirect(reverse('index'))

class UserLogin(View):

    def get(self, request):
        ctx = {}

        # 如果已经登录了
        if request.user.is_active:
            return redirect(reverse('index'))

        # slogan彩蛋
        if request.GET.get('changeslogan') == 'true':
            ctx['slogan'] = '除了我的无知外，我其实一无所知'
            ctx['author'] = '苏格拉底'
            return JsonResponse(ctx)

        ctx['slogan'] = '勇气是多一分钟的无惧'
        ctx['author'] = '美国将军·巴顿'
        return render(request, 'ftkuser/login.html', ctx)

    @ratelimit(key='ip', rate='3/m')
    def post(self, request):

        was_limited = getattr(request, 'limited', False)
        if was_limited:
            return JsonResponse({'msg': '您的登录尝试过于频繁，请稍后再试...'}, status=500)

        ctx = {}
        username = request.POST.get('u')
        password = request.POST.get('p')
        user = authenticate(username=username,password=password)
        if user is not None and user.is_active:
            try:
                login(request, user)
            except Exception,e:
                return JsonResponse({'msg': '登录失败'},status=500)
            else:
                if user.is_staff:
                    return JsonResponse({'next': reverse('admin:index')})
                else:
                    return JsonResponse({'next': reverse('index')})
        else:
            return JsonResponse({'msg': '用户名或密码错误'}, status=500)