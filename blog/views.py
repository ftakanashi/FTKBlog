# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django_redis import get_redis_connection
from django.shortcuts import render, redirect, reverse
from django.http.response import Http404, JsonResponse
from django.http import QueryDict
from django.views.generic import View
from django.core.cache import cache
from django.utils.decorators import method_decorator
from pure_pagination import Paginator
from ratelimit.decorators import ratelimit
from .models import Post, Category, Tag, Comment

import json
import re
import traceback

redis = get_redis_connection('default')
# Create your views here.

class IndexView(View):

    @ratelimit(key='ip',rate='1/1s')
    def get(self, request):

        was_limited = getattr(request,'limited',False)
        if was_limited:
            return ''

        try:
            page = int(request.GET.get('page', '1'))
        except Exception, e:
            page = 1

        sCate = request.GET.get('category')
        if sCate is not None:
            posts = Post.objects.filter(category__cate_id=sCate).filter(status=0)
        else:
            posts = Post.objects.filter(status=0)

        posts = posts.order_by('-is_top', '-update_time')
        for post in posts:
            # post.read_count = cache.hget('blog:read_count',post.post_uuid,-1)
            post.read_count = redis.hget('blog:read_count',post.post_uuid) or -1

        p = Paginator(posts, 10, request=request)
        paged_posts = p.page(page)

        categories = Category.objects.all()
        for category in categories:
            category.count = category.in_category_posts.count()

        tags = Tag.objects.all()
        for tag in tags:
            tag.count = tag.in_tag_posts.count()

        ctx = {}
        ctx['posts'] = paged_posts
        ctx['categoryList'] = categories
        ctx['tagList'] = tags
        return render(request, 'index.html', ctx)


class NewPostView(View):
    CACHE_KEY = 'blog:post_cache'
    CACHE_TTL = 600

    @classmethod
    def markdown2text(cls, markdown):
        p = re.compile('[\\\_\[\]\#\+\!]|[\`\*\-]{3,}|^>')
        return p.sub('', markdown)

    @method_decorator(login_required)
    def get(self, request):
        categoryList = Category.objects.all()
        tagList = Tag.objects.all()
        return render(request, 'blog/new.html', locals())

    @method_decorator(login_required)
    def put(self, request):
        put = QueryDict(request.body)
        act = put.get('act')
        if not act or act not in ('save', 'load', 'clear'):
            return JsonResponse({'msg': '非法的操作类型'}, status='500')
        if act == 'save':
            try:
                content = put.get('content')
                cache.set(self.CACHE_KEY, content, self.CACHE_TTL)
            except Exception, e:
                print traceback.format_exc(e)
                return JsonResponse({'msg': '自动保存失败'}, status=500)
            else:
                return JsonResponse({'msg': '自动保存成功'})
        elif act == 'load':
            try:
                fetch = cache.get(self.CACHE_KEY)
                if fetch is None:
                    return JsonResponse({'msg': '抱歉，没有找到自动保存'}, status=404)
            except Exception, e:
                print traceback.format_exc(e)
                return JsonResponse({'msg': '获取缓存内容失败'}, status=500)
            else:
                return JsonResponse(
                        {'msg': '获取缓存内容成功', 'content': fetch,
                         'time': self.CACHE_TTL - cache.ttl(self.CACHE_KEY)})
        elif act == 'clear':
            cache.delete(self.CACHE_KEY)

    @method_decorator(login_required)
    def post(self, request):
        # ctx = {}
        try:
            postInfo = {}
            postInfo['title'] = request.POST.get('title')
            postInfo['content'] = request.POST.get('content')
            postInfo['category'] = Category.objects.get(cate_id=request.POST.get('category'))
            postInfo['abstract'] = self.markdown2text(postInfo['content'])[:150]
            postInfo['is_top'] = request.POST.get('is_top') == 'true'
            postInfo['is_reprint'] = request.POST.get('is_reprint') == 'true'
            postInfo['reprint_src'] = request.POST.get('reprint_src')
            postInfo['status'] = '0' if request.POST.get('is_publish') == 'true' else '1'
            tags = json.loads(request.POST.get('tag'))
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '上传内容错误'}, status=500)

        processFlag = False
        try:
            post = Post(**postInfo)
            post.save()
            processFlag = True
            for tag in tags:
                if isinstance(tag, unicode):
                    tag = int(tag)
                post.tag.add(Tag.objects.get(tag_id=tag))
        except Exception, e:
            print traceback.format_exc(e)
            if processFlag:
                postUrl = reverse('detail', kwargs={'uuid': post.post_uuid})
                redis.hset('blog:read_count',post.post_uuid,0)
                # cache.set('read_count:%s' % post.post_uuid,0)
                # cache.persist('read_count:%s' % post.post_uuid)
                return JsonResponse({'msg': '添加文章成功，但是关联标签失败', 'next': postUrl})
            else:
                return JsonResponse({'msg': '添加文章失败'}, status=500)
        else:
            # cache.set('read_count:%s' % post.post_uuid,0)
            # cache.persist('read_count:%s' % post.post_uuid)
            redis.hset('blog:read_count',post.post_uuid,0)    # todo redis中记录要随着模型删除也删除（后台）2.搞个crontab让redis定期入库
            postUrl = reverse('detail', kwargs={'uuid': post.post_uuid})
            return JsonResponse({'next': postUrl})


class PostView(View):
    @ratelimit(key='ip',rate='1/5s')
    def get(self, request, uuid):
        ctx = {}

        was_limited = getattr(request, 'limited', False)
        if was_limited:
            return ''

        try:
            postId = int(uuid)
            url = reverse('detail', kwargs={'uuid': unicode(Post.objects.get(post_id=postId).post_uuid)})
            return redirect(url)
        except ValueError, e:
            pass

        try:
            post = Post.objects.get(post_uuid=uuid)
        except Post.DoesNotExist, e:
            return Http404()
        else:
            # ctx['read_count'] = cache.incr('read_count:%s' % uuid)
            ctx['read_count'] = redis.hincrby('blog:read_count',uuid,1)
            ctx['post'] = post

        return render(request, 'blog/post.html', ctx)

    @method_decorator(login_required)
    def delete(self, request, uuid):
        delete = QueryDict(request.body)
        target = delete.get('target')
        if not request.user.is_superuser:
            return JsonResponse({'msg': '你的IP已经被记录了，你想什么滴干活？！'},status=500)
        if target == 'comment':
            comment_uuid = delete.get('uuid')
            try:
                comment = Comment.objects.get(comment_uuid=comment_uuid)
            except Comment.DoesNotExist,e:
                return JsonResponse({'msg': '没有找到要删除的评论'},status=404)
            try:
                comment.delete()
            except Exception,e:
                return JsonResponse({'msg': '删除失败'},status=500)
            return JsonResponse({'msg': ''})

        else:
            # 删除post直接在页面上实现掉真的好吗…安全方面考虑
            return JsonResponse({'msg':'你想干什么[发呆]'},status=500)



class CommentView(View):

    def get(self, request):

        ctx = {}

        uuid = request.GET.get('post_uuid')

        try:
            if not uuid: raise Exception()
            post = Post.objects.get(post_uuid=uuid)
        except Exception:
            return render(request ,'error.html', {'error_msg':'没有找到相关文章链接'})

        try:
            pre = request.GET.get('pre')
            replyFloor = int(request.GET.get('rf',-1))
            replyComment = None
            if replyFloor != -1:
                replyComment = Comment.objects.get(in_post=post,floor=replyFloor)
        except Exception:
            return render(request, 'error.html', {'error_msg': '没有找到要回复的评论'})

        ctx['pre'] = pre
        ctx['post_uuid'] = uuid
        ctx['reply_comment'] = replyComment

        return render(request, 'blog/comment.html', ctx)

    @ratelimit(key='ip',rate='1/1s')
    def post(self, request):

        was_limited = getattr(request, 'limited', False)
        if was_limited:
            return JsonResponse({'msg': '请求过于频繁，请稍候再试'}, status=403)

        post_uuid = request.POST.get('pid')
        author = request.POST.get('author')
        email = request.POST.get('email')
        title = request.POST.get('title')
        content = request.POST.get('content')
        if not author or not title or not content or not post_uuid:
            return JsonResponse({'msg': '别闹，填正确的信息'},status=500)
        if author == '博主' and not request.user.is_active:
            return JsonResponse({'msg': '你确定没在冒充我？…'},status=500)

        try:
            post = Post.objects.get(post_uuid=post_uuid)
        except Post.DoesNotExist,e:
            return JsonResponse({'msg': '没有找到相关文章'},status=404)

        try:
            reply_to = request.POST.get('replyto').strip()
            comment = Comment(author=author, email=email, title=title, content=content, in_post=post, reply_to=reply_to)
            comment.floor = comment.in_post.comments.count() + 1
            comment.save()
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '评论失败了...'},status=500)
        else:
            return JsonResponse({})
