# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import json
import os
import shutil
import traceback

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render,reverse
from django.views import View
from django.http import QueryDict,JsonResponse,Http404, StreamingHttpResponse
from django_redis import get_redis_connection

from blog.models import Category, Tag, Dict, Post, Comment, Message
from blog.views import NewPostView
from ftkuser.models import AccessControl
# Create your views here.
redis = get_redis_connection('default')

class IndexView(View):

    def get(self, request):
        ctx = {}
        urcInfo = []
        for cid in redis.lrange(settings.UNREAD_COMMENTS_KEY,0,-1):
            try:
                comment = Comment.objects.get(comment_id=cid)
            except Comment.DoesNotExist,e:
                redis.lrem(settings.UNREAD_COMMENTS_KEY,0,cid)
                continue
            else:
                urcInfo.append(comment)

        urmInfo = []
        for mid in redis.lrange(settings.UNREAD_MESSAGE_KEY,0,-1):
            try:
                message = Message.objects.get(message_id=mid)
            except Message.DoesNotExist,e:
                redis.lrem(settings.UNREAD_MESSAGE_KEY,0,mid)
                continue
            else:
                urmInfo.append(message)

        ctx['access_count'] = redis.get(settings.ACCESS_COUNT_KEY)
        ctx['urcInfo'] = urcInfo
        ctx['urmInfo'] = urmInfo
        return render(request, 'myadmin/dashboard.html', ctx)

    def post(self, request):
        act = request.POST.get('act')
        if act == 'ignore-urc':
            while redis.llen(settings.UNREAD_COMMENTS_KEY) > 0:
                redis.lpop(settings.UNREAD_COMMENTS_KEY)
            return JsonResponse({})
        elif act == 'ignore-urm':
            while redis.llen(settings.UNREAD_MESSAGE_KEY) > 0:
                redis.lpop(settings.UNREAD_MESSAGE_KEY)
            return JsonResponse({})

        return JsonResponse({'msg': '无效的申请动作'},status=500)

class CategoryManage(View):
    def get(self, request):
        ctx = {}
        if request.GET.get('type') == 'edit':
            cate_id = request.GET.get('pk')
            try:
                category = Category.objects.get(cate_id=cate_id)
            except Category.DoesNotExist,e:
                return render(request, 'error.html', {'err_msg': '没有找到相关分类'})
            else:
                ctx['category'] = category
                ctx['type'] = 'edit'
                return render(request, 'myadmin/modulemanage/category/edit.html', ctx)
        elif request.GET.get('type') == 'add':
            ctx['type'] = 'add'
            return render(request,'myadmin/modulemanage/category/add.html', ctx)

        return render(request, 'myadmin/modulemanage/category/view.html', ctx)

    def post(self, request):
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            category = Category(name=name,description=description)
            category.save()
        except Exception,e:
            return JsonResponse({'msg': '新增失败\n%s' % unicode(e)},status=500)
        else:
            return JsonResponse({})

    def delete(self, request):
        DELETE = QueryDict(request.body)
        try:
            category = Category.objects.get(cate_id=DELETE.get('target'))
        except Category.DoesNotExist,e:
            return JsonResponse({'msg': '没有找到相关分类'}, status=404)
        try:
            category.delete()
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除失败'}, status=500)
        else:
            return JsonResponse({})

    def put(self, request):
        PUT = QueryDict(request.body)
        try:
            category = Category.objects.get(cate_id=PUT.get('cate_id'))
        except Category.DoesNotExist,e:
            return JsonResponse({'msg': '没有找到相关分类'}, status=404)
        try:
            for field in ('cate_id','name','description'):
                setattr(category,field,PUT.get(field))
        except Exception,e:
            return JsonResponse({'msg': '更新失败'}, status=500)
        else:
            category.save()
            return JsonResponse({})

class TagManage(View):
    def get(self, request):
        ctx = {}
        if request.GET.get('type') == 'edit':
            tag_id = request.GET.get('pk')
            try:
                tag = Tag.objects.get(tag_id=tag_id)
            except Category.DoesNotExist,e:
                return render(request, 'error.html', {'err_msg': '没有找到相关分类'})
            else:
                ctx['tag'] = tag
                ctx['type'] = 'edit'
                return render(request, 'myadmin/modulemanage/tag/edit.html', ctx)
        elif request.GET.get('type') == 'add':
            ctx['type'] = 'add'
            return render(request,'myadmin/modulemanage/tag/add.html', ctx)

        return render(request, 'myadmin/modulemanage/tag/view.html', ctx)

    def post(self, request):
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            tag = Tag(name=name,description=description)
            tag.save()
        except Exception,e:
            return JsonResponse({'msg': '新增失败\n%s' % unicode(e)},status=500)
        else:
            return JsonResponse({})


    def delete(self, request):
        DELETE = QueryDict(request.body)
        try:
            tag = Tag.objects.get(tag_id=DELETE.get('target'))
        except Tag.DoesNotExist,e:
            return JsonResponse({'msg': '没有找到相关标签'}, status=404)
        try:
            tag.delete()
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除失败'}, status=500)
        else:
            return JsonResponse({})

    def put(self, request):
        PUT = QueryDict(request.body)
        try:
            tag = Tag.objects.get(tag_id=PUT.get('tag_id'))
        except Tag.DoesNotExist,e:
            return JsonResponse({'msg': '没有找到相关标签'}, status=404)
        try:
            for field in ('tag_id','name','description'):
                setattr(tag,field,PUT.get(field))
        except Exception,e:
            return JsonResponse({'msg': '更新失败'}, status=500)
        else:
            tag.save()
            return JsonResponse({})

class DictManage(View):

    def get(self, request):
        ctx = {}
        if request.GET.get('type') == 'add':
            return render(request, 'myadmin/modulemanage/dict/add.html', ctx)

        dictInfo = collections.defaultdict(dict)
        for item in Dict.objects.all():
            dictInfo[item.category][item.key] = item.value

        ctx['dictInfo'] = dict(dictInfo)
        return render(request, 'myadmin/modulemanage/dict/dict.html',ctx)

    def post(self, request):
        try:
            key = request.POST.get('key')
            value = request.POST.get('value')
            category = request.POST.get('category')
            dictItem = Dict(key=key,value=value,category=category)
            dictItem.save()
        except Exception,e:
            return JsonResponse({'msg': '新增失败\n%s' % unicode(e)},status=500)
        else:
            return JsonResponse({})

    def delete(self, request):
        DELETE = QueryDict(request.body)
        try:
            dict = Dict.objects.get(key=DELETE.get('key'))
        except Dict.DoesNotExist,e:
            return JsonResponse({'msg': '没有找到相关标签'}, status=404)
        try:
            dict.delete()
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除失败'}, status=500)
        else:
            return JsonResponse({})

    def put(self, request):
        ctx = {}
        PUT = QueryDict(request.body)
        try:
            item = Dict.objects.get(key=PUT.get('key'))
        except Dict.DoesNotExist,e:
            return JsonResponse({'msg': '没有找到相关字典项'}, status=404)
        item.value = PUT.get('value')
        try:
            item.save()
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '更改字典项值失败'}, status=500)

        return JsonResponse({})

class PostManange(View):
    REDIS = redis
    READ_COUNT_KEY = settings.READ_COUNT_KEY
    CACHE_KEY = settings.CACHE_KEY
    CACHE_TTL = 86400

    def get(self, request):
        ctx = {}
        ctx['uuid'] = request.GET.get('uuid')
        if request.GET.get('type') == 'edit':
            post_uuid = request.GET.get('pk')
            try:
                post = Post.objects.get(post_uuid=post_uuid)
            except Post.DoesNotExist,e:
                return render(request, 'error.html', {'error_msg':'没有找到相关文章','error_title': '发生错误'})

            post.tags = ' '.join([a.name for a in post.tag.all()])
            ctx['post'] = post
            ctx['type'] = 'edit'
            ctx['categoryList'] = Category.objects.all().order_by('name')
            ctx['tagList'] = Tag.objects.all().order_by('name')
            return render(request, 'blog/new.html', ctx)

        return render(request, 'myadmin/modulemanage/post/view.html', ctx)


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

    def delete(self, request):
        DELETE = QueryDict(request.body)
        try:
            post = Post.objects.get(post_uuid=DELETE.get('target'))
        except Post.DoesNotExist,e:
            return JsonResponse({'msg': '没有找到相关文章'}, status=404)
        try:
            post.delete()
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除失败'},status=500)
        try:    # 和Post关联但是没有反应到模型层中的数据，需要手动额外删除
            # 删除redis中read_count缓存
            back = self.REDIS.hdel(self.READ_COUNT_KEY,post.post_uuid)
            if back is None:
                raise Exception('No such key in redis found: %s' % self.READ_COUNT_KEY + post.post_uuid)

            # 删除文章中上传的图片
            postImgDir = os.path.join(settings.IMG_UPLOAD_DIR, str(post.post_uuid))
            if os.path.isdir(postImgDir):
                shutil.rmtree(postImgDir)

        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '文章相关数据删除失败'}, status=501)

        return JsonResponse({})

    def post(self, request):

        try:
            post = Post.objects.get(post_uuid=request.POST.get('post_uuid'))
        except Post.DoesNotExist,e:
            return JsonResponse({'msg': '没有找到相关文章'}, status=404)

        try:
            post.title = request.POST.get('title')
            post.content = request.POST.get('content')
            post.is_top = request.POST.get('is_top') == 'true'
            post.is_reprint = request.POST.get('is_reprint') == 'true'
            post.reprint_src = request.POST.get('reprint_src')

            if request.POST.get('is_publish') == 'true':
                post.status = '0'
            else:
                post.status = '1'

            post.abstract = NewPostView.markdown2text(post.content)[:150]    # 这个方法定义在NewPostView里了…
            post.save()

        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '保存失败'}, status=500)

        try:
            category = Category.objects.get(cate_id=request.POST.get('category'))
            tags = json.loads(request.POST.get('tag'))
            post.category = category
            for tag in post.tag.all():
                post.tag.remove(tag)
            for tag in tags:
                try:
                    tag_obj = Tag.objects.get(tag_id=tag)
                except Tag.DoesNotExist,e:
                    print traceback.format_exc(e)
                    continue
                post.tag.add(tag_obj)
            post.save()
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '关联文章分类/标签失败'},status=500)

        return JsonResponse({'next': reverse('detail',kwargs={'uuid': post.post_uuid})})

class CommentManage(View):

    def get(self, request):
        ctx = {}
        return render(request, 'myadmin/modulemanage/comment/view.html', ctx)

    def delete(self, request):
        DELETE = QueryDict(request.body)
        try:
            comment = Comment.objects.get(comment_id=DELETE.get('target'))
        except Comment.DoesNotExist,e:
            return JsonResponse({'msg': '没有找到相关分类'}, status=404)
        try:
            comment.delete()
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除失败'}, status=500)
        else:
            return JsonResponse({})

class MessageManage(View):

    def get(self, request):
        ctx = {}
        return render(request, 'myadmin/modulemanage/message/view.html', ctx)

    def delete(self, request):
        DELETE = QueryDict(request.body)
        try:
            message = Message.objects.get(message_id=DELETE.get('target'))
        except Comment.DoesNotExist,e:
            return JsonResponse({'msg': '没有找到相关留言'}, status=404)
        try:
            message.delete()
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除失败'}, status=500)
        else:
            return JsonResponse({})

class AccessControlManage(View):

    def get(self, request):
        ctx = {}

        if request.GET.get('type') == 'edit':
            try:
                ac = AccessControl.objects.get(ac_id=request.GET.get('pk'))
            except AccessControl.DoesNotExist,e:
                raise Http404

            ctx['ac'] = ac
            return render(request,'myadmin/modulemanage/accesscontrol/edit.html',ctx)
        elif request.GET.get('type') == 'add':
            return render(request, 'myadmin/modulemanage/accesscontrol/edit.html')

        return render(request, 'myadmin/modulemanage/accesscontrol/view.html', ctx)

    def delete(self, request):
        DELETE = QueryDict(request.body)
        try:
            ac = AccessControl.objects.get(ac_id=DELETE.get('target'))
        except AccessControl.DoesNotExist,e:
            return JsonResponse({'msg': '没有找到相关权限记录'},status=404)
        try:
            ac.delete()
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除失败'},status=500)

        return JsonResponse({})

    def post(self, request):
        try:
            source_ip = request.POST.get('source_ip')
            control_type = request.POST.get('control_type')
            domain = request.POST.get('domain')
            ac = AccessControl(source_ip=source_ip, control_type=control_type, domain=domain)
            ac.save()
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '新增规则失败'},status=500)
        else:
            return JsonResponse({})

    def put(self, request):
        PUT = QueryDict(request.body)
        try:
            ac_id = PUT.get('ac_id')
            ac = AccessControl.objects.get(ac_id=ac_id)
        except AccessControl.DoesNotExist,e:
            return JsonResponse({'msg': '没有找到相关的权限控制记录'},status=404)

        try:
            ac.source_ip = PUT.get('source_ip')
            ac.control_type = PUT.get('control_type')
            ac.domain = PUT.get('domain')
            ac.save()
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '更新权限控制记录失败'},status=500)

        return JsonResponse({})

class BackupDownloadManage(View):

    def _adaptSize(self, bytes):
        k = round(bytes / 1024.0, 4)
        if k < 1:
            return '%sB' % bytes
        m = round(k / 1024.0, 4)
        if m < 1:
            return '%sKB' % k
        g = round(m / 1024.0, 4)
        if g < 1:
            return '%sMB' % m

        return '%sGB' % g

    def get(self, request):
        ctx = {}
        dbBackupDir = os.path.join(settings.PROJECT_ROOT, 'backup', 'db')
        uploadBackupDir = os.path.join(settings.PROJECT_ROOT, 'backup', 'upload')
        links = {'db': [], 'upload': []}
        for dbback in os.listdir(dbBackupDir):
            links['db'].append({
                'link': 'db__' + dbback,
                 'name': dbback,
                 'size': self._adaptSize(os.stat(os.path.join(dbBackupDir, dbback)).st_size)
            })
        for uploadBack in os.listdir(uploadBackupDir):
            links['upload'].append({
                'link': 'upload__' + uploadBack,
                'name': uploadBack,
                'size': self._adaptSize(os.stat(os.path.join(uploadBackupDir, uploadBack)).st_size)
            })

        links['db'].sort(key=lambda x: x['name'])
        links['upload'].sort(key=lambda x: x['name'])
        ctx['links'] = links
        return render(request, 'myadmin/modulemanage/backupdownload.html', ctx)

def backup_download(request, fn):

    try:
        type,filename = fn.split('__',1)
        if not type or not filename or type not in ('db','upload'):
            raise Exception('Invalid request')
    except Exception,e:
        return render(request, 'error.html', {'error_msg': '请求的URL似乎有错'})

    d = os.path.join(settings.PROJECT_ROOT, 'backup', type)
    filename = os.path.join(d, filename)
    if not os.path.isfile(filename):
        return render(request, 'error.html', {'error_msg': '没有找到相关文件'})

    def file_iterator(filename, chunk_size=512):
        with open(filename, 'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    response = StreamingHttpResponse(file_iterator(filename))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(filename)

    return response