# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.conf import settings
from django_redis import get_redis_connection
from pure_pagination import Paginator
from ratelimit.decorators import ratelimit
from blog.models import Post

import math
import traceback
# Create your views here.


class SearchView(View):

    ES_CLIENT =  settings.ES_CLIENT
    PAGE_SIZE = 2
    REDIS = get_redis_connection('default')

    @ratelimit(key='ip',rate='1/5s')
    def get(self, request):
        ctx = {}

        kw = request.GET.get('kw')
        logic = request.GET.get('logic')

        if getattr(request,'limited',False) and (kw and logic):
            ctx['msg'] = '请求过于频繁，请稍候重试'
            return render(request, 'search/index.html',ctx)

        try:
            page = int(request.GET.get('page','1'))
        except Exception,e:
            page = 1

        if kw is None or logic is None:
            return render(request, 'search/index.html',ctx)

        kws = kw.split(' ')
        highlightConf = {
            'number_of_fragments': 3,
            'fragment_size': 80,
            'fields': {
                'title': {
                    'pre_tags': '<span class="highlight">',
                    'post_tags': '</span>'
                },
                'content': {
                    'pre_tags': '<span class="highlight">',
                    'post_tags': '</span>'
                }
            }
        }
        filterConf = [{'term': {'status': '0'}}]
        if logic == '0':
            # AND模式
            shouldBoostDict = self._setBoost(kws, pivot=3, step=len(kws)*0.1)
            mustBoostDict = self._setBoost(kws)

            plan = {
                '_source': False,
                'query': {
                    'bool': {
                        'should': [{'match': {'title': {'query': word, 'boost': boost}}} for word,boost in shouldBoostDict.iteritems()],
                        'must': [{'match': {'content': {'query': word, 'boost': boost}}} for word,boost in mustBoostDict.iteritems()]
                    }
                },
                'highlight': highlightConf,
                'size': 9999,
                # 'from': (page-1) * self.PAGE_SIZE
            }
        elif logic == '1':
            # OR模式
            conditionList = []
            titleBoost = self._setBoost(kws,pivot=5)
            contentBoost = self._setBoost(kws)
            for kw in kws:
                conditionList.append({'match': {'title': {'query': kw, 'boost': titleBoost.get(kw,0)}}})
                conditionList.append({'match': {'content': {'query': kw, 'boost': contentBoost.get(kw,0)}}})
            plan = {
                '_source': False,
                'query': {
                    'bool': {
                        'should': conditionList
                    }
                },
                'highlight': highlightConf,
                'size': 9999,
                # 'from': (page-1) * self.PAGE_SIZE,
                'min_score': 1
            }
        else:
            return render(request, 'error.html', {'error_msg': '','error_title': '未知的逻辑类型'})
        try:
            if not request.user.is_active:
                plan['query']['bool']['filter'] = filterConf
            res = self.ES_CLIENT.search(index=settings.ELASTICSEARCH_INDEX,doc_type='post_document',body=plan)
        except Exception,e:
            print traceback.format_exc(e)
            return render(request,'error.html',{'error_msg':'请稍候再试','error_title': '后台搜索发生错误'})

        # import json
        # print json.dumps(res,indent=4)

        if res.get('timed_out'):
            return render(request, 'error.html', {'error_msg': '请稍后再试试', 'error_title': '查询超时'})
        ctx['time_cost'] = res.get('took')
        total = res['hits']['total']
        candidates = []
        for hit in res['hits']['hits']:
            candidate = Post.objects.get(post_id=hit['_id'])
            candidate.highlight = hit['highlight']
            candidate.score = hit['_score']
            candidate.read_count = self.REDIS.hget(settings.READ_COUNT_KEY,candidate.post_uuid)
            candidates.append(candidate)


        posts = sorted(candidates, key=lambda x: x.score,reverse=True)
        p = Paginator(posts, 10, request=request)
        paged_post = p.page(page)
        ctx['posts'] = paged_post
        ctx['total'] = total

        ctx['current_page'] = page

        return render(request, 'search/index.html', ctx)

    def _setBoost(self, keywords,step=0.2,pivot=1):
        map = {}
        total = len(keywords)
        if total % 2 == 0:
            for i,word in enumerate(keywords):
                map[word] = math.exp(pivot + ((total/2) - i) * step)
        else:
            for i,word in enumerate(keywords):
                map[word] = math.exp(pivot + ((total//2) - i) * step)

        return map