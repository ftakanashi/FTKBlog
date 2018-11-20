# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django_redis import get_redis_connection
from django.shortcuts import render, redirect, reverse
from django.http.response import Http404, JsonResponse
from django.http import QueryDict
from django.db.models import QuerySet
from django.views.generic import View
from django.utils.decorators import method_decorator
from pure_pagination import Paginator
from ratelimit.decorators import ratelimit
from .models import Post, Category, Tag, Comment, Dict, Message
from .utils import CodeGenerator

import json
import os
import re
import time
import traceback

from uuid import uuid4

redis = get_redis_connection('default')


# Create your views here.

class IndexView(View):
    @ratelimit(key='ip', rate='1/2s')
    def get(self, request):

        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ','error_title': ''})

        try:
            page = int(request.GET.get('page', '1'))
        except Exception, e:
            page = 1

        posts = Post.objects.filter(status=0)
        sCate = request.GET.get('category')
        sTag = request.GET.get('tag')

        if sCate is not None:
            posts = posts.filter(category__cate_id=sCate)
        elif sTag is not None:
            try:
                tag = Tag.objects.get(tag_id=sTag)
            except Tag.DoesNotExist,e:
                pass
            else:
                posts = tag.in_tag_posts.all()
        # if sCate is not None:
        #     posts = Post.objects.filter(category__cate_id=sCate).filter(status=0)
        # else:
        #     posts = Post.objects.filter(status=0)

        posts = posts.order_by('-is_top', '-update_time')
        # for post in posts:
        #     post.read_count = redis.hget(settings.READ_COUNT_KEY, post.post_uuid) or -1

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
        ctx['categoryList'] = sorted(categories, key=lambda x: x.count, reverse=True)
        ctx['tagList'] = sorted(tags, key=lambda x: x.count, reverse=True)
        ctx['pageDictInfo'] = {q.key: q.value for q in Dict.objects.filter(category='index_page')}
        ctx['quickLinks'] = {q.key: q.value for q in Dict.objects.filter(category='quick_links')}
        if not request.user.is_superuser:
            # cache.incr(settings.ACCESS_COUNT_KEY)
            redis.incr(settings.ACCESS_COUNT_KEY)

        return render(request, 'index.html', ctx)


class NewPostView(View):
    CACHE_KEY = settings.CACHE_KEY
    CACHE_TTL = 3600

    @classmethod
    def markdown2text(cls, markdown):
        p = re.compile('[\\\_\[\]\#\+\!]|[\`\*\-]{3,}|^>')
        return p.sub('', markdown)

    def get(self, request):
        categoryList = Category.objects.all()
        tagList = Tag.objects.all()
        return render(request, 'blog/new.html', locals())

    def put(self, request):
        put = QueryDict(request.body)
        act = put.get('act')
        if not act or act not in ('save', 'load', 'clear'):
            return JsonResponse({'msg': '非法的操作类型'}, status='500')
        if act == 'save':
            try:
                content = put.get('content')
                post_uuid = put.get('post_uuid')
                # cache.set(self.CACHE_KEY, content, self.CACHE_TTL)
                redis.hset(self.CACHE_KEY,'content',content)
                redis.hset(self.CACHE_KEY,'post_uuid',post_uuid)
                redis.expire(self.CACHE_KEY,self.CACHE_TTL)
            except Exception, e:
                print traceback.format_exc(e)
                return JsonResponse({'msg': '自动保存失败'}, status=500)
            else:
                return JsonResponse({'msg': '自动保存成功'})
        elif act == 'load':
            try:
                # fetch = cache.get(self.CACHE_KEY)
                fetch = {'content': redis.hget(self.CACHE_KEY,'content'),'post_uuid': redis.hget(self.CACHE_KEY,'post_uuid')}
                if fetch['content'] is None and fetch['post_uuid'] is None:
                    return JsonResponse({'msg': '抱歉，没有找到自动保存'}, status=404)
            except Exception, e:
                print traceback.format_exc(e)
                return JsonResponse({'msg': '获取缓存内容失败'}, status=500)
            else:
                return JsonResponse(
                        {'msg': '获取缓存内容成功', 'content': fetch['content'],
                         'post_uuid': fetch['post_uuid'],
                         'time': self.CACHE_TTL - redis.ttl(self.CACHE_KEY)})
        elif act == 'clear':
            redis.delete(self.CACHE_KEY)

    def post(self, request):
        # ctx = {}
        try:
            postInfo = {}
            postInfo['title'] = request.POST.get('title')
            postInfo['post_uuid'] = request.POST.get('post_uuid')
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
                redis.hset(settings.READ_COUNT_KEY, post.post_uuid, 0)
                return JsonResponse({'msg': '添加文章成功，但是关联标签失败', 'next': postUrl})
            else:
                return JsonResponse({'msg': '添加文章失败'}, status=500)
        else:
            redis.hset(settings.READ_COUNT_KEY, post.post_uuid, 0)
            postUrl = reverse('detail', kwargs={'uuid': post.post_uuid})
            return JsonResponse({'next': postUrl})


class PostView(View):
    @ratelimit(key='ip', rate='1/5s')
    def get(self, request, uuid):
        ctx = {}

        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ','error_title': ''})

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
            ctx['read_count'] = redis.hincrby(settings.READ_COUNT_KEY, uuid, 1)
            ctx['post'] = post

        return render(request, 'blog/post.html', ctx)

    @ratelimit(key='ip', rate='1/5s', block=True)
    def post(self, request, uuid):
        act = request.POST.get('act')
        if act == 'great':
            post_uuid = uuid
            direct = request.POST.get('direct')
            post = Post.objects.get(post_uuid=post_uuid)
            if direct == '+':
                post.greats += 1
            elif direct == '-':
                post.greats -= 1
            else:
                pass
            post.save()
            return JsonResponse({})

        return JsonResponse({'msg': '你到底想要干什么呀？'}, status=500)

    @method_decorator(login_required)
    @ratelimit(key='ip', rate='1/5s', block=True)
    def delete(self, request, uuid):
        '''
        在页面上删除的请求。需要指出target。其实后续可以直接整合到后台的视图中去
        '''
        delete = QueryDict(request.body)
        target = delete.get('target')
        if not request.user.is_superuser:    # 拒绝非管理员的删除请求
            return JsonResponse({'msg': '你想什么滴干活？！'}, status=500)
        if target == 'comment':
            comment_uuid = delete.get('uuid')
            try:
                comment = Comment.objects.get(comment_uuid=comment_uuid)
            except Comment.DoesNotExist, e:
                return JsonResponse({'msg': '没有找到要删除的评论'}, status=404)
            try:
                comment.delete()
            except Exception, e:
                print traceback.format_exc(e)
                return JsonResponse({'msg': '删除失败'}, status=500)
            return JsonResponse({'msg': ''})

        else:
            # 删除post直接在页面上实现掉真的好吗…安全方面考虑
            return JsonResponse({'msg': '你想干什么[发呆]'}, status=500)


class CommentView(View):

    # VERI_CODE_EXPIRE = 60
    VERI_CODE_KEY = settings.VERI_CODE_KEY

    @ratelimit(key='ip', rate='1/s')
    def get(self, request):
        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ','error_title': ''})

        ctx = {}

        uuid = request.GET.get('post_uuid')
        try:
            if not uuid: raise Exception()
            post = Post.objects.get(post_uuid=uuid)
        except Exception:
            return render(request, 'error.html', {'error_msg': '根本没有你想评论的文章啊(•̀へ •́ ╮ )'})

        try:
            pre = request.GET.get('pre')
            replyFloor = int(request.GET.get('rf', -1))
            replyComment = None
            if replyFloor != -1:
                replyComment = Comment.objects.get(in_post=post, floor=replyFloor)
        except Exception:
            return render(request, 'error.html', {'error_msg': '没有找到要回复的评论'})

        ctx['pre'] = pre
        ctx['post_uuid'] = uuid
        ctx['reply_comment'] = replyComment

        # codeGenerator = CodeGenerator()
        # ctx['veri_code'] = codeGenerator.generateCode()
        # veriCodeUuid = str(uuid4())
        # ctx['veri_code_uuid'] = veriCodeUuid
        # correctText = codeGenerator.getText()
        # redis.set(self.VERI_CODE_KEY % veriCodeUuid, correctText)
        # redis.expire(self.VERI_CODE_KEY % veriCodeUuid, self.VERI_CODE_EXPIRE)

        return render(request, 'blog/comment.html', ctx)

    @ratelimit(key='ip', rate='1/s', block=True)
    def post(self, request):

        veri_code = request.POST.get('veri_code')
        veri_code_uuid = request.POST.get('veri_code_uuid')
        if not veri_code or not veri_code_uuid:
            return JsonResponse({'msg': '是不是忘记输验证码了?'}, status=500)

        correctText = redis.get(self.VERI_CODE_KEY % veri_code_uuid)
        if not correctText:
            return JsonResponse({'msg': '验证码过期咯'}, status=502)
        if correctText.lower() != veri_code.lower():
            redis.delete(self.VERI_CODE_KEY % veri_code_uuid)
            return JsonResponse({'msg': '验证码输错啦'}, status=502)
        else:
            redis.delete(self.VERI_CODE_KEY % veri_code_uuid)

        post_uuid = request.POST.get('pid')
        author = request.POST.get('author')
        email = request.POST.get('email')
        title = request.POST.get('title')
        content = request.POST.get('content')
        source_ip = request.META.get('REMOTE_ADDR')

        if not author or not title or not content or not post_uuid:
            return JsonResponse({'msg': '别闹，填正确的信息'}, status=500)
        if author == '博主' and not request.user.is_active:
            return JsonResponse({'msg': '你确定没在冒充我？…'}, status=500)

        try:
            post = Post.objects.get(post_uuid=post_uuid)
        except Post.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关文章'}, status=404)

        try:
            reply_to = request.POST.get('replyto').strip()
            comment = Comment(author=author, email=email, title=title, content=content, in_post=post, reply_to=reply_to,
                              source_ip=source_ip)
            comment.floor = comment.in_post.comments.count() + 1
            comment.save()
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '评论失败了...'}, status=500)
        else:
            if not request.user.is_superuser:
                redis.rpush(settings.UNREAD_COMMENTS_KEY, comment.comment_id)
            return JsonResponse({})

class MessageView(View):

    VERI_CODE_KEY = settings.VERI_CODE_KEY

    @ratelimit(key='ip', rate='1/s')
    def get(self, request):

        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ','error_title': ''})

        ctx = {}
        ctx['posts'] = Post.objects.filter(status='0')

        return render(request, 'blog/message.html', ctx)

    @ratelimit(key='ip', rate='1/5s', block=True)
    def post(self, request):

        veriCode = request.POST.get('veriCode')
        veriCodeUuid = request.POST.get('veriCodeUuid')
        if not veriCode or not veriCodeUuid:
            return JsonResponse({'msg': '是不是忘记输验证码了?'}, status=500)

        correctText = redis.get(self.VERI_CODE_KEY % veriCodeUuid)
        if not correctText:
            return JsonResponse({'msg': '验证码过期咯'}, status=502)
        if correctText.lower() != veriCode.lower():
            redis.delete(self.VERI_CODE_KEY % veriCodeUuid)
            return JsonResponse({'msg': '验证码输错啦'}, status=502)
        else:
            redis.delete(self.VERI_CODE_KEY % veriCodeUuid)

        author = request.POST.get('author')
        contact = request.POST.get('contact')
        title = request.POST.get('title')
        content = request.POST.get('content')
        sourceIp = request.META.get('REMOTE_ADDR')
        relatePostId = request.POST.get('relatePost')
        try:
            if relatePostId:
                post = Post.objects.get(post_uuid=relatePostId)
            else:
                post = None
        except Post.DoesNotExist,e:
            return JsonResponse({'msg': '没有找到对应文章，可能已经被删除了o(╥﹏╥)o'}, status=404)
        try:
            message = Message(author=author,content=content,title=title,contact=contact,relate_post=post,source_ip=sourceIp)
            message.save()
            redis.rpush(settings.UNREAD_MESSAGE_KEY,message.message_id)
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '提交留言失败'},status=500)

        return JsonResponse({})

class VeriCodeView(View):

    VERI_CODE_KEY = settings.VERI_CODE_KEY
    VERI_CODE_EXPIRE = 60

    @ratelimit(key='ip', rate='1/5s')
    def get(self, request):

        if getattr(request, 'limited', False):
            return JsonResponse({'msg': '你点得太快了(╯‵□′)╯︵┻━┻'}, status=500)

        ctx = {}

        oldCodeUuid = request.GET.get('veri_code_uuid')
        redis.delete(self.VERI_CODE_KEY % oldCodeUuid)

        codeGenerator = CodeGenerator()
        newCodeUuid = str(uuid4())
        ctx['veri_code'] = codeGenerator.generateCode()
        ctx['veri_code_uuid'] = newCodeUuid
        redis.set(self.VERI_CODE_KEY % newCodeUuid, codeGenerator.getText())
        redis.expire(self.VERI_CODE_KEY % newCodeUuid, self.VERI_CODE_EXPIRE)

        return JsonResponse(ctx)

@csrf_exempt
def editormd_upload(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': 0,
            'message': '错误的请求方法'
        },status=500)

    fi_obj = request.FILES.get('editormd-image-file')

    if fi_obj is None:
        return JsonResponse({'success': 0,'message': '上传体未找到图片文件对象'})

    guid = request.GET.get('guid')
    guid_dir = os.path.join(settings.IMG_UPLOAD_DIR,guid)
    if not os.path.isdir(guid_dir):
        os.mkdir(guid_dir)

    fi_name = '%s-%s' % (str(int(time.time() * 1000)), fi_obj.name)
    fi_path = os.path.join(guid_dir, fi_name)
    if os.path.isfile(fi_name):
        return JsonResponse({'success': 0, 'message': '服务器中已经存在同名文件'})
    try:
        f = open(fi_path,'wb')
        for chunk in fi_obj.chunks():
            f.write(chunk)
        f.close()
    except Exception,e:
        return JsonResponse({'success': 0, 'message': '生成文件失败：%s' % unicode(e)})
    try:
        return JsonResponse({
            'success': 1,
            'msg': '上传成功',
            'url': '/static/upload/post-image/%s/%s' % (guid,fi_name)
        })
    except Exception,e:
        return JsonResponse({'success': 0, 'message': '上传失败...'})
