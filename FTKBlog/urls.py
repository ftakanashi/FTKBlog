# -*- coding:utf-8 -*-
"""FTKBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
# from django.contrib import admin
from django.shortcuts import redirect, reverse, render
from django.http import JsonResponse

from ratelimit.decorators import ratelimit

def index(request):
    return redirect(reverse('index'))

@ratelimit(key='ip', rate='1/s')
def about(request):
    ctx = {}

    if getattr(request, 'limited', False):
        return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ','error_title': ''})

    return render(request,'about.html',ctx)

@ratelimit(key='ip', rate='1/s')
def error_test(request):
    ctx = {
        'error_title': '',
        'error_msg': '这个页面是专门用来玩儿这个小飞机的…'
    }
    return render(request,'error.html',ctx)

def handler_404(request):
    ctx = {
        'error_title': '未找到页面',
        'error_msg': '这个页面已经飘到M78星云了'
    }
    return render(request,'error.html',ctx, status=404)

def handler_403(request):
    if getattr(request, 'limited', False):
        return JsonResponse({'msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ'},status=403)

    ctx = {
        'error_title': '无权限',
        'error_msg': '可能是因为未登录或者请求过于频繁'
    }
    return render(request, 'error.html', ctx, status=403)

urlpatterns = [
    url('^$', index),
    # url(r'^admin/', admin.site.urls),
    url(r'^my-admin/', include('myadmin.urls'),name='myadmin'),
    url(r'^blog/', include('blog.urls')),
    url(r'^user/',include('ftkuser.urls')),
    url(r'^search/',include('search.urls')),
    url(r'^about/', about, name='about'),
    url(r'^error/', error_test, name='errortest'),
    url(r'^accounts/login/', lambda x: redirect(reverse('login')))
]

handler403 = handler_403
handler404 = handler_404
