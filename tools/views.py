# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from ratelimit.decorators import ratelimit

# Create your views here.

class BiologyRhythmView(View):

    @ratelimit(key='ip', rate='1/1s')
    def get(self, request):

        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

        ctx = {}
        return render(request, 'tools/biorhy.html', ctx)