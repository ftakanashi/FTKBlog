# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import logging
import string
import traceback
import uuid as uuid_gen

from django.shortcuts import render, reverse, redirect
from django.http import QueryDict, JsonResponse
from django.views import View
from django.conf import settings
from ratelimit.decorators import ratelimit
from pure_pagination import Paginator
from django_redis import get_redis_connection

from models import Paper, ResearchTag, PaperComment, Author, Reference
from blog.models import Dict

logger = logging.getLogger('django')
redis = get_redis_connection('default')

# Create your views here.

class IndexView(View):
    def _do_filter(self, datasets, request):
        title = request.GET.get('title')
        try:
            year = int(request.GET.get('year'))
        except Exception as e:
            year = None
        origin = request.GET.get('origin')
        try:
            tags = [int(t) for t in request.GET.get('tags').split('|')]
        except Exception as e:
            tags = []
        author = request.GET.get('author')

        if title:
            datasets = datasets.filter(title__contains=title)
        if year:
            datasets = datasets.filter(publish_time__year=year)
        if origin:
            datasets = datasets.filter(publish_origin__icontains=origin)
        if author:
            datasets = datasets.filter(author__name__icontains=author)
        if len(tags) > 0:
            datasets = datasets.intersection(Paper.objects.filter(tag__research_tag_id__in=tags))

        return datasets

    @ratelimit(key='ip', rate='1/1s')
    def get(self, request):

        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

        ctx = {}
        try:
            page = int(request.GET.get('p', '1'))
            page_size = int(request.GET.get('ps', '10'))
        except Exception as e:
            page = 1
            page_size = 10

        papers = Paper.objects.all()
        papers = self._do_filter(papers, request)

        p = Paginator(papers, page_size, request=request)
        papers = p.page(page)

        if len(papers.object_list) == 0:
            ctx['flash_message'] = '没有发现任何符合情况的结果'
            # ctx['papers'] = Paper.objects.all()
        else:
            ctx['papers'] = papers

        ctx['tags'] = ResearchTag.objects.all().order_by('name')
        ctx['authors'] = Author.objects.all().order_by('name')
        return render(request, 'paperdb/index.html', ctx)


class PaperView(View):
    LATEST_KEY = settings.LATEST_NEWPAPER_UUID_KEY
    CACHE_KEY = settings.PAPER_CACHE_KEY
    CACHE_TTL = 3600

    @ratelimit(key='ip', rate='1/1s')
    def get(self, request):
        ctx = {}
        pk = request.GET.get('pk')
        ctx['authors'] = Author.objects.all().order_by('name')
        ctx['tags'] = ResearchTag.objects.all().order_by('name')
        ctx['papers'] = Paper.objects.all().order_by('title')
        try:
            autosave_interval = Dict.objects.get(key='autosaveInterval').value
        except Exception as e:
            pass
        else:
            ctx['autosave_interval'] = autosave_interval

        if pk is None:
            if redis.exists(self.LATEST_KEY):
                pk = redis.get(self.LATEST_KEY)
            else:
                pk = str(uuid_gen.uuid4())
            ctx['paper_uuid'] = pk

            return render(request, 'paperdb/new.html', ctx)

        else:
            try:
                paper = Paper.objects.get(paper_uuid=pk)
            except Exception as e:
                return render(request, 'error.html', {'error_msg': '没有找到相关论文', 'error_title': '4 0 4!!'})
            ctx['paper'] = paper
            ctx['paper_uuid'] = pk
            return render(request, 'paperdb/new.html', ctx)

    @ratelimit(key='ip', rate='1/5s', block=True)
    def post(self, request):
        param = QueryDict(request.body)

        uuid = param.get('uuid')
        title = param.get('title')
        time = param.get('time')
        origin = param.get('origin')
        _authors = param.getlist('authors')
        link = param.get('link')
        _tags = param.getlist('tags')
        content = param.get('content')
        refer_to = param.getlist('reference')
        score = param.get('score')

        try:
            year, month = time.split('-')
            year, month = int(year), int(month)
            publish_time = datetime.date(year, month, 1)
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return JsonResponse({'msg': '提供的日期{}有误'.format(time)}, status=500)


        for _tag in _tags:
            try:
                _tag = int(_tag)
                _ = ResearchTag.objects.get(research_tag_id=_tag)
            except Exception as e:
                logger.error(traceback.format_exc(e))
                return JsonResponse({'msg': '错误的标签{}'.format(_tag)}, status=500)
        tags = ResearchTag.objects.filter(research_tag_id__in=[int(_t) for _t in _tags])


        author_ids = []
        for _author in _authors:
            if _author.isdigit():
                author_ids.append(int(_author))
            elif Author.objects.filter(name=_author).exists():
                a = Author.objects.get(name=_author).author_id
                author_ids.append(a)
            else:
                a = Author(name=_author)
                a.save()
                author_ids.append(a.author_id)

        authors = Author.objects.filter(author_id__in=author_ids)

        try:
            score = int(score)
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return JsonResponse({'msg': '错误的评分分数格式'}, status=500)

        if not Paper.objects.filter(paper_uuid=uuid).exists():
            # 新建的场合
            try:
                comment = PaperComment(content=content)
                comment.save()
                paper = Paper(paper_uuid=uuid,title=title, publish_origin=origin, publish_time=publish_time,
                              author=authors, link=link, tag=tags, comment=comment, self_score=score)
                paper.save()
                redis.set(self.LATEST_KEY, str(uuid_gen.uuid4()))
            except Exception as e:
                logger.error(traceback.format_exc(e))
                return JsonResponse({'msg': '保存失败'}, status=500)
            else:
                return JsonResponse({'next': reverse('paperdb.detail', kwargs={'paper_uuid': paper.paper_uuid})})

        try:
            # 编辑的场合
            paper = Paper.objects.get(paper_uuid=uuid)
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return JsonResponse({'msg': '错误的uuid/未找到相关论文记录'}, status=404)
        else:
            paper.title = title
            paper.publish_time = publish_time
            paper.publish_origin = origin
            paper.author = authors
            paper.link = paper.link
            paper.tag = tags
            paper.self_score = score

            try:
                paper.save()
            except Exception as e:
                logger.error(traceback.format_exc(e))
                return JsonResponse({'msg': '保存失败'}, status=500)

            if paper.comment is None:
                if content != '':
                    comment = PaperComment(content=content)
                    comment.save()
                    paper.comment = comment
                    paper.save()
            elif content != paper.comment.content.replace('\r\n', '\n'):    # traditional下的换行符出入
                paper.comment.content = content
                paper.comment.save()

        for refer_to_paper in Paper.objects.filter(paper_uuid__in=refer_to):
            if not Reference.objects.filter(reference_src=paper, reference_trg=refer_to_paper).exists():
                reference = Reference(reference_src=paper, reference_trg=refer_to_paper)
                reference.save()

        return JsonResponse({'next': reverse('paperdb.detail', kwargs={'paper_uuid': paper.paper_uuid})})

    def put(self, request):
        param = QueryDict(request.body)
        act = param.get('act')
        uuid = param.get('uuid')
        if act is None:
            return JsonResponse({'msg': '无请求动作'}, status=500)
        if uuid is None:
            return JsonResponse({'msg': '未上送UUID'}, status=500)

        cache_key = self.CACHE_KEY.format(uuid)

        if act == 'save':
            title = param.get('title')
            content = param.get('content')
            try:
                redis.hset(cache_key, 'title', title)
                redis.hset(cache_key, 'content', content)
                redis.expire(cache_key, self.CACHE_TTL)
            except Exception as e:
                logger.error(traceback.format_exc(e))
                return JsonResponse({'msg': '自动保存失败'}, status=500)
            else:
                return JsonResponse({'msg': '自动保存成功'})

        elif act == 'load':
            try:
                if not redis.exists(cache_key) or redis.hget(cache_key, 'content') is None:
                    return JsonResponse({'msg': '未找到自动保存的内容'}, status=404)
                fetch = {
                    'title': redis.hget(cache_key, 'title'),
                    'content': redis.hget(cache_key, 'content'),
                    'time': self.CACHE_TTL - redis.ttl(cache_key)
                }
            except Exception as e:
                logger.error(traceback.format_exc(e))
                return JsonResponse({'msg': '读取缓存失败'}, status=500)
            else:
                data = {
                    'msg': '读取缓存成功'
                }
                data.update(fetch)
                return JsonResponse(data)


class PaperDetailView(View):
    @ratelimit(key='ip', rate='1/1s')
    def get(self, request, paper_uuid):
        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

        try:
            paper = Paper.objects.get(paper_uuid=paper_uuid)
        except Exception as e:
            logger.error('获取论文信息失败:\n{}'.format(traceback.format_exc(e)))
            return render(request, 'error.html', {'error_msg': '没有找到相关论文', 'error_title': '4 0 4!!'})

        ctx = {}
        ctx['paper'] = paper
        ctx['quickLinks'] = {q.key: q.value for q in Dict.objects.filter(category='quick_links')}

        return render(request, 'paperdb/detail.html', ctx)


class PaperReferenceView(View):
    @ratelimit(key='ip', rate='1/1s')
    def get(self, request, paper_uuid):
        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

        try:
            ctx = {}
            paper = Paper.objects.get(paper_uuid=paper_uuid)
        except Exception as e:
            logger.error('获取论文信息失败:\n{}'.format(traceback.format_exc(e)))
            return render(request, 'error.html', {'error_msg': '没有找到相关论文', 'error_title': '4 0 4!!'})

        ctx['paper'] = paper
        return render(request, 'paperdb/reference.html', ctx)

    @ratelimit(key='ip', rate='1/5s', block=True)
    def post(self, request, paper_uuid):
        try:
            paper = Paper.objects.get(paper_uuid=paper_uuid)
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return JsonResponse({'msg': '错误的uuid: {}'.format(paper_uuid)}, status=500)

        def to_apa_form(paper):
            authors = '. '.join([a.name for a in paper.author.all()])
            year = paper.publish_time.year
            title = paper.title if len(paper.title) <= 30 else (paper.title[:30] + '...')
            origin = paper.publish_origin
            apa_str = '{}.({}).\n{}'.format(authors, year, title)
            if origin != 'unknown':
                apa_str += '\n{}'.format(origin)

            return apa_str

        nodes, links = [], []
        center = {'id': paper.paper_uuid, 'name': to_apa_form(paper), 'value': 999, 'label': {'color': 'red'}}
        included_paper = [paper, ]
        nodes.append(center)
        for ref_rel in paper.reference.all():
            ref = ref_rel.reference_trg
            included_paper.append(ref)

            nodes.append({
                'id': ref.paper_uuid,
                'name': to_apa_form(ref),
                'label': {'color': 'blue'}
            })

            links.append({
                'source': ref.paper_uuid,
                'target': paper.paper_uuid
            })


        for ref_rel in paper.be_referred.all():
            ref = ref_rel.reference_src
            if ref not in included_paper:
                nodes.append({
                    'id': ref.paper_uuid,
                    'name': to_apa_form(ref),
                    'label': {'color': 'green'}
                })

            links.append({
                'source': paper.paper_uuid,
                'target': ref.paper_uuid
            })

        response_data = {'nodes': nodes, 'links': links}
        return JsonResponse(response_data)