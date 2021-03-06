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
from .models import Post, Category, Tag, Comment, Dict, Message, PostMeta
from .utils import CodeGenerator

import datetime
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
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

        try:
            page = int(request.GET.get('page', '1'))
        except Exception, e:
            page = 1

        posts = Post.objects.filter(status=0)
        sCate = request.GET.get('category')
        sTag = request.GET.get('tag')

        # 私密分类不展示
        try:
            private_category = Category.objects.get(name='私密')
        except Category.DoesNotExist as e:
            private_category = None
        else:
            posts = posts.exclude(category=private_category)

        if sCate is not None:
            posts = posts.filter(category__cate_id=sCate)
        elif sTag is not None:
            try:
                tag = Tag.objects.get(tag_id=sTag)
            except Tag.DoesNotExist, e:
                pass
            else:
                posts = tag.in_tag_posts.all()

        top_posts = posts.filter(is_top=1).order_by('title')
        posts = posts.order_by('-edit_time')

        p = Paginator(posts, 10, request=request)
        paged_posts = p.page(page)

        if private_category is not None and not request.user.is_superuser:
            categories = Category.objects.all().exclude(name='私密')
        else:
            categories = Category.objects.all()
        for category in categories:
            category.count = category.in_category_posts.count()

        tags = Tag.objects.all()
        for tag in tags:
            tag.count = tag.in_tag_posts.count()

        ctx = {}
        ctx['topPosts'] = top_posts
        ctx['posts'] = paged_posts
        ctx['categoryList'] = sorted(categories, key=lambda x: x.count, reverse=True)
        ctx['tagList'] = sorted(tags, key=lambda x: x.count, reverse=True)
        ctx['pageDictInfo'] = {q.key: q.value for q in Dict.objects.filter(category='index_page')}
        ctx['quickLinks'] = {q.key: q.value for q in Dict.objects.filter(category='quick_links')}

        if not request.user.is_superuser:
            # 非管理员的首页访问，访问记录在后台
            redis.incr(settings.ACCESS_COUNT_KEY)
            aip = request.META.get('REMOTE_ADDR')
            found_flag = False
            total_access = 0

            for acc_rec in redis.lrange(settings.ACCESS_IP_QUEUE, 0, -1):
                if acc_rec.split('|')[0] == aip:
                    redis.lrem(settings.ACCESS_IP_QUEUE, 0, acc_rec)
                    found_flag = True
                    total_access = int(acc_rec.split('|')[2])
                    break

            if not found_flag and redis.llen(settings.ACCESS_IP_QUEUE) >= 10:
                redis.lpop(settings.ACCESS_IP_QUEUE)

            redis.rpush(settings.ACCESS_IP_QUEUE, '{}|{}|{}'.format(aip,
                                                                    datetime.datetime.now().strftime(
                                                                        '%Y-%m-%d %H:%M:%S'),
                                                                    total_access + 1))

        return render(request, 'index.html', ctx)


class SiteMemoView(View):
    SITE_MEMO_KEY = settings.SITE_MEMO_KEY

    @ratelimit(key='ip', rate='1/1s')
    def get(self, request):
        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

        ctx = {}

        memos = sorted(redis.hgetall(self.SITE_MEMO_KEY).items(), key=lambda x: float(x[0]))

        def adapt_content(c):
            # return c.replace(str('\n'), str('<br/>'))
            return c

        ctx['memos'] = [(i + 1, m[0], adapt_content(m[1])) for i, m in enumerate(memos[1:])]

        return render(request, 'blog/sitememo.html', ctx)

    @ratelimit(key='ip', rate='1/5s', block=True)
    def post(self, request):
        content = request.POST.get('content')
        try:
            redis.hset(self.SITE_MEMO_KEY, str(time.time()), content)
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '提交备忘录失败'}, status=500)
        else:
            return JsonResponse({})

    @ratelimit(key='ip', rate='1/5s', block=True)
    def delete(self, request):
        delete = QueryDict(request.body)

        if not request.user.is_superuser:
            return JsonResponse({'msg': '拒绝非管理员的删除请求'}, status=403)

        try:
            id = delete.get('id')
            redis.hdel(self.SITE_MEMO_KEY, id)
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除失败'}, status=500)
        else:
            return JsonResponse({})

    @ratelimit(key='ip', rate='1/5s', block=True)
    def put(self, request):
        PUT = QueryDict(request.body)
        memo_id = PUT.get('id')
        if memo_id is None:
            return JsonResponse({'msg': '上送ID有误'}, status=400)
        if not redis.hexists(self.SITE_MEMO_KEY, memo_id):
            return JsonResponse({'msg': '未找到相关备忘录记录'}, status=404)

        try:
            content = PUT.get('content')
            redis.hset(self.SITE_MEMO_KEY, str(time.time()), content)
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '保存新备忘录失败'}, status=500)

        try:
            redis.hdel(self.SITE_MEMO_KEY, memo_id)
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除旧备忘录失败'}, status=500)

        return JsonResponse({})


class NewPostView(View):
    LATEST_KEY = settings.LATEST_NEWPOST_UUID_KEY
    CACHE_KEY = settings.CACHE_KEY
    CACHE_TTL = 3600

    @classmethod
    def markdown2text(cls, markdown):
        p = re.compile('[\\\_\[\]\#\+\!]|[\`\*\-]{3,}|^>')
        return p.sub('', markdown)

    def get(self, request):
        try:
            autosave_interval = Dict.objects.get(key='autosaveInterval').value
        except Exception, e:
            pass
        categoryList = Category.objects.all()
        tagList = Tag.objects.all().order_by('name')
        quickLinks = Dict.objects.filter(category='quick_links')
        return render(request, 'blog/new.html', locals())

    def put(self, request):
        put = QueryDict(request.body)
        act = put.get('act')
        if not act or act not in ('save', 'load', 'clear', 'latest'):
            return JsonResponse({'msg': '非法的操作类型'}, status='500')
        if act == 'save':
            try:
                title = put.get('title')
                content = put.get('content')
                post_uuid = put.get('post_uuid')
                if not post_uuid:
                    return JsonResponse({'msg': '未上送uuid'}, status=500)
                cache_key = self.CACHE_KEY.format(post_uuid)
                redis.hset(cache_key, 'title', title)
                redis.hset(cache_key, 'content', content)
                redis.expire(cache_key, self.CACHE_TTL)
            except Exception, e:
                print traceback.format_exc(e)
                return JsonResponse({'msg': '自动保存失败'}, status=500)
            else:
                return JsonResponse({'msg': '自动保存成功'})
        elif act == 'load':
            try:
                post_uuid = put.get('post_uuid')
                if not post_uuid:
                    return JsonResponse({'msg': '未上送uuid'}, status=500)
                cache_key = self.CACHE_KEY.format(post_uuid)
                if not redis.exists(cache_key) or redis.hget(cache_key, 'content') is None:
                    return JsonResponse({'msg': '抱歉，没有找到自动保存'}, status=404)
                fetch = {
                    'title': redis.hget(cache_key, 'title'),
                    'content': redis.hget(cache_key, 'content'),
                    'post_uuid': post_uuid
                }
            except Exception, e:
                print traceback.format_exc(e)
                return JsonResponse({'msg': '获取缓存内容失败'}, status=500)
            else:
                return JsonResponse(
                        {'msg': '获取缓存内容成功', 'content': fetch['content'],
                         'post_uuid': fetch['post_uuid'], 'title': fetch['title'],
                         'time': self.CACHE_TTL - redis.ttl(cache_key)})
        elif act == 'clear':
            post_uuid = put.get('post_uuid')
            if not post_uuid:
                return JsonResponse({'msg': '未上送uuid'}, status=500)
            # redis.delete(self.CACHE_KEY)
            cache_key = self.CACHE_KEY.format(post_uuid)
            redis.delete(cache_key)
        elif act == 'latest':
            post_uuid = put.get('post_uuid')
            if not post_uuid:
                return JsonResponse({'msg': '未上送uuid'}, status=500)

            latest_newpost_uuid = redis.get(self.LATEST_KEY)
            if latest_newpost_uuid is None:
                redis.set(self.LATEST_KEY, post_uuid)
                return JsonResponse({'uuid': post_uuid})
            else:
                return JsonResponse({'uuid': latest_newpost_uuid})
        return JsonResponse({})

    def post(self, request):

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
        typeFlag = request.POST.get('flag', 'new')
        try:
            if typeFlag == 'new':    # 新建
                post = Post(**postInfo)
            elif typeFlag == 'edit':    # 编辑已有文章
                post = Post.objects.get(post_uuid=postInfo['post_uuid'])
                for k,v in postInfo.iteritems():
                    setattr(post, k, v)
            else:
                return JsonResponse({'msg': '错误的flag种类[{}]'.format(typeFlag)}, status=500)
            post.save()

            # 落地到库，缓存中的latest_new_post_uuid可以删除
            redis.delete(self.LATEST_KEY)

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
                return JsonResponse({'msg': '添加文章失败：{}'.format(unicode(e))}, status=500)
        else:
            if typeFlag == 'new':
                redis.hset(settings.READ_COUNT_KEY, post.post_uuid, 0)
            postUrl = reverse('detail', kwargs={'uuid': post.post_uuid})
            return JsonResponse({'next': postUrl})


class PostView(View):
    @ratelimit(key='ip', rate='1/5s')
    def get(self, request, uuid):
        ctx = {}

        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

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
            if post.category.name == '私密' and not request.user.is_superuser:
                return render(request, 'error.html', {'error_title': '无法查看', 'error_msg': '本文隶属于保密局管辖，无查看权限o(*￣︶￣*)o'})

            if post.status == '0':
                ctx['read_count'] = redis.hincrby(settings.READ_COUNT_KEY, uuid, 1)
            else:
                ctx['read_count'] = redis.hget(settings.READ_COUNT_KEY, uuid)
            ctx['post'] = post
            ctx['quickLinks'] = {q.key: q.value for q in Dict.objects.filter(category='quick_links')}

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
        if not request.user.is_superuser:  # 拒绝非管理员的删除请求
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


class PostMetaView(View):
    @ratelimit(key='ip', rate='1/1s')
    def get(self, request):
        ctx = {}

        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

        try:
            uuid = request.GET.get('pk')
            if not uuid:
                raise Post.DoesNotExist
            post = Post.objects.get(post_uuid=uuid)
        except Post.DoesNotExist, e:
            return Http404()

        try:
            ctx['meta'] = post.metas.all()[0]
        except IndexError, e:
            ctx['meta'] = None

        ctx['post'] = post
        return render(request, 'blog/meta.html', ctx)

    @ratelimit(key='ip', rate='1/5s', block=True)
    def post(self, request):
        uuid = request.POST.get('uuid')
        meta_content = request.POST.get('meta')

        try:
            post = Post.objects.get(post_uuid=uuid)
        except Post.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相应文章'}, status=404)

        try:
            meta = post.metas.all()[0]
            meta.content = meta_content
        except IndexError, e:
            meta = PostMeta(title=post.title, content=meta_content, in_post=post)

        try:
            meta.save()
        except Exception, e:
            return JsonResponse({'msg': '保存Meta失败'}, status=400)

        return JsonResponse({})


class CommentView(View):
    # VERI_CODE_EXPIRE = 60
    VERI_CODE_KEY = settings.VERI_CODE_KEY

    @ratelimit(key='ip', rate='1/s')
    def get(self, request):
        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

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
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

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
        except Post.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到对应文章，可能已经被删除了o(╥﹏╥)o'}, status=404)
        try:
            message = Message(author=author, content=content, title=title, contact=contact, relate_post=post,
                              source_ip=sourceIp)
            message.save()
            redis.rpush(settings.UNREAD_MESSAGE_KEY, message.message_id)
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '提交留言失败'}, status=500)

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
        }, status=500)

    fi_obj = request.FILES.get('editormd-image-file')

    if fi_obj is None:
        return JsonResponse({'success': 0, 'message': '上传体未找到图片文件对象'})

    guid = request.GET.get('guid')
    guid_dir = os.path.join(settings.IMG_UPLOAD_DIR, guid)
    try:
        if not os.path.isdir(guid_dir):
            os.mkdir(guid_dir)
    except Exception as e:
        print traceback.format_exc(e)
        return JsonResponse({'success': 0, 'message': '创建图片缓存目录失败'.format(guid_dir)})

    fi_name = '%s-%s' % (str(int(time.time() * 1000)), fi_obj.name)
    fi_path = os.path.join(guid_dir, fi_name)
    if os.path.isfile(fi_name):
        return JsonResponse({'success': 0, 'message': '服务器中已经存在同名文件'})
    try:
        f = open(fi_path, 'wb')
        for chunk in fi_obj.chunks():
            f.write(chunk)
        f.close()
    except Exception, e:
        print traceback.format_exc(e)
        return JsonResponse({'success': 0, 'message': '生成文件失败：%s' % unicode(e)})

    return JsonResponse({
        'success': 1,
        'msg': '上传成功',
        'url': '/static/upload/post-image/%s/%s' % (guid, fi_name)
    })
