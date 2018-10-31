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
from django.contrib import admin
from django.shortcuts import redirect, reverse, render

def index(request):
    return redirect(reverse('index'))

def about(request):
    ctx = {
        'error_title': '未找到页面',
        'error_msg': '这个页面已经飘到M78星云了'
    }
    return render(request,'error.html',ctx)

def handler_404(request):
    ctx = {
        'error_title': '未找到页面',
        'error_msg': '这个页面已经飘到M78星云了'
    }
    return render(request,'error.html',ctx)

urlpatterns = [
    url('^$', index),
    url(r'^admin/', admin.site.urls),
    url(r'^blog/', include('blog.urls')),
    url(r'^user/',include('ftkuser.urls')),
    url(r'^about/', about, name='about')
]

handler404 = handler_404