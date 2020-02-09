# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import traceback

from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.views import View

from ratelimit.decorators import ratelimit

from .models import WyzCoup

# Create your views here.
class WyzCoupView(View):

    @ratelimit(key='ip', rate='1/1s')
    def get(self, request):
        ctx = {}

        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

        coup_uuid = request.GET.get('coup_uuid', '')
        try:
            if coup_uuid == '':
                raise WyzCoup.DoesNotExist
            wyz_coup = WyzCoup.objects.get(coup_uuid=coup_uuid)
        except WyzCoup.DoesNotExist as e:
            return render(request, 'wyzcoup/error.html')

        wyz_coup.format_create_time = wyz_coup.create_time.strftime('%Y-%m-%d')
        if wyz_coup.expire_time is not None:
            wyz_coup.format_expire_time = wyz_coup.expire_time.strftime('%Y-%m-%d')
        if wyz_coup.consume_time is not None:
            wyz_coup.format_consume_time = wyz_coup.consume_time.strftime('%Y-%m-%d')

        ctx['coup'] = wyz_coup

        return render(request, 'wyzcoup/coup.html', ctx)

    def post(self, request):
        coup_uuid = request.POST.get('uuid')

        try:
            coup = WyzCoup.objects.get(coup_uuid=coup_uuid)
        except WyzCoup.DoesNotExist as e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '没有找到这张好人卡呀┓( ´∀` )┏'}, status=404)

        if coup.coup_status == '1':
            return JsonResponse({'msg': '这张好人卡已经被用过了呀，亲我一下再给你一张⁄(⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄'}, status=500)
        elif coup.coup_status == '2':
            return JsonResponse({'msg': '这张好人卡已经过期了呀，亲我一下给你延期⁄(⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄'}, status=500)
        else:
            note = request.POST.get('note')
            coup.coup_status = '1'
            coup.consume_time = datetime.datetime.now()
            coup.coup_note = note
            try:
                coup.save()
            except Exception as e:
                print traceback.format_exc(e)
                return JsonResponse({'msg': '修改卡状态失败'}, status=500)

        return JsonResponse({'next': reverse('wyzcoup.coup.receipt') + '?pk={}'.format(coup_uuid)})

class WyzCoupRepView(View):

    def get(self, request):
        ctx = {}
        coup_uuid = request.GET.get('pk')
        try:
            coup = WyzCoup.objects.get(coup_uuid=coup_uuid)
        except WyzCoup.DoesNotExist as e:
            return render(request, 'wyzcoup/error.html', ctx)
        if coup.coup_status != '1':
            return redirect(reverse('wyzcoup.coup') + '?pk={}'.format(coup_uuid))

        coup.format_consume_time = coup.consume_time.strftime('%Y-%m-%d')
        ctx['coup'] = coup
        return render(request, 'wyzcoup/receipt.html', ctx)