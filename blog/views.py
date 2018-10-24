# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.views.generic import View
# Create your views here.

class IndexView(View):
    def get(self, request):

        ctx = {'nums': range(20)}
        return render(request, 'index.html', ctx)
