# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import datetime
import json
import logging
import os
import qrcode
import random
import shutil
import subprocess
import time
import traceback
from PIL import Image, ImageFont, ImageDraw

from django.conf import settings
from django.shortcuts import render, reverse
from django.views import View
from django.http import QueryDict, JsonResponse, Http404, StreamingHttpResponse
from django_redis import get_redis_connection
from django.db.models import Q

from blog.models import Category, Tag, Dict, Post, Comment, Message
from blog.views import NewPostView
from paperdb.models import Paper, ResearchTag, Reference, Author
from ftkuser.models import AccessControl
from wyzcoup.models import WyzCoup

# Create your views here.
redis = get_redis_connection('default')
logger = logging.getLogger('django')


class IndexView(View):
    def get(self, request):
        ctx = {}

        urcInfo = []
        for cid in redis.lrange(settings.UNREAD_COMMENTS_KEY, 0, -1):
            try:
                comment = Comment.objects.get(comment_id=cid)
            except Comment.DoesNotExist, e:
                redis.lrem(settings.UNREAD_COMMENTS_KEY, 0, cid)
                continue
            else:
                urcInfo.append(comment)

        urmInfo = []
        for mid in redis.lrange(settings.UNREAD_MESSAGE_KEY, 0, -1):
            try:
                message = Message.objects.get(message_id=mid)
            except Message.DoesNotExist, e:
                redis.lrem(settings.UNREAD_MESSAGE_KEY, 0, mid)
                continue
            else:
                urmInfo.append(message)

        # accessIp = redis.lrange(settings.ACCESS_IP_QUEUE, 0, -1)

        accessIp = []
        for data in redis.lrange(settings.ACCESS_IP_QUEUE, 0, -1):
            ip, time, count = data.split('|')
            accessIp.append({'ip': ip, 'time': time, 'count': count})

        lastBackupTime = redis.get(settings.LAST_BACKUP_KEY)
        if lastBackupTime is None:
            logger.warning('未找到上次备份下载时间')
            lastBackupTime = '未找到上次备份下载时间'
            lastBackupGap = 0
        else:
            lastBackupTime = datetime.datetime.fromtimestamp(float(lastBackupTime))
            lastBackupGap = (datetime.datetime.now() - lastBackupTime).total_seconds()
            lastBackupTime = lastBackupTime.strftime('%Y年%m月%d日 %H:%M:%S'.encode('utf-8'))

        p = subprocess.Popen('ps -ef | grep elasticsearch | grep -v grep', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out.strip() == '':
            ctx['found_elastic'] = False
        else:
            ctx['found_elastic'] = True

        ctx['access_count'] = redis.get(settings.ACCESS_COUNT_KEY)
        ctx['last_backup'] = lastBackupTime
        ctx['last_backup_gap'] = lastBackupGap > (86400 * 3)
        ctx['access_ip'] = accessIp
        ctx['site_switches'] = Dict.objects.filter(category='site_switch')
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
        elif act == 'site-switch':
            switchName = request.POST.get('name')
            switchTo = request.POST.get('value')
            try:
                item = Dict.objects.get(key=switchName)
                item.value = str(switchTo)
                item.save()
            except Dict.DoesNotExist, e:
                return JsonResponse({'msg': '没有找到相关开关'}, status=404)
            except Exception, e:
                print traceback.format_exc(e)
                return JsonResponse({'msg': '设置开关失败'}, status=500)
            else:
                return JsonResponse({})

        return JsonResponse({'msg': '无效的申请动作'}, status=500)


class CategoryManage(View):
    def get(self, request):
        ctx = {}
        if request.GET.get('type') == 'edit':
            cate_id = request.GET.get('pk')
            try:
                category = Category.objects.get(cate_id=cate_id)
            except Category.DoesNotExist, e:
                return render(request, 'error.html', {'err_msg': '没有找到相关分类'})
            else:
                ctx['category'] = category
                ctx['type'] = 'edit'
                return render(request, 'myadmin/modulemanage/category/edit.html', ctx)
        elif request.GET.get('type') == 'add':
            ctx['type'] = 'add'
            return render(request, 'myadmin/modulemanage/category/add.html', ctx)

        return render(request, 'myadmin/modulemanage/category/view.html', ctx)

    def post(self, request):
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            category = Category(name=name, description=description)
            category.save()
        except Exception, e:
            return JsonResponse({'msg': '新增失败\n%s' % unicode(e)}, status=500)
        else:
            return JsonResponse({})

    def delete(self, request):
        DELETE = QueryDict(request.body)
        try:
            category = Category.objects.get(cate_id=DELETE.get('target'))
        except Category.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关分类'}, status=404)
        try:
            category.delete()
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除失败'}, status=500)
        else:
            return JsonResponse({})

    def put(self, request):
        PUT = QueryDict(request.body)
        try:
            category = Category.objects.get(cate_id=PUT.get('cate_id'))
        except Category.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关分类'}, status=404)
        try:
            for field in ('cate_id', 'name', 'description'):
                setattr(category, field, PUT.get(field))
        except Exception, e:
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
            except Category.DoesNotExist, e:
                return render(request, 'error.html', {'err_msg': '没有找到相关分类'})
            else:
                ctx['tag'] = tag
                ctx['type'] = 'edit'
                return render(request, 'myadmin/modulemanage/tag/edit.html', ctx)
        elif request.GET.get('type') == 'add':
            ctx['type'] = 'add'
            return render(request, 'myadmin/modulemanage/tag/add.html', ctx)

        return render(request, 'myadmin/modulemanage/tag/view.html', ctx)

    def post(self, request):
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            tag = Tag(name=name, description=description)
            tag.save()
        except Exception, e:
            return JsonResponse({'msg': '新增失败\n%s' % unicode(e)}, status=500)
        else:
            return JsonResponse({})

    def delete(self, request):
        DELETE = QueryDict(request.body)
        try:
            tag = Tag.objects.get(tag_id=DELETE.get('target'))
        except Tag.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关标签'}, status=404)
        try:
            tag.delete()
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除失败'}, status=500)
        else:
            return JsonResponse({})

    def put(self, request):
        PUT = QueryDict(request.body)
        try:
            tag = Tag.objects.get(tag_id=PUT.get('tag_id'))
        except Tag.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关标签'}, status=404)
        try:
            for field in ('tag_id', 'name', 'description'):
                setattr(tag, field, PUT.get(field))
        except Exception, e:
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
        for item in Dict.objects.exclude(category__in=('site_switch',)):
            dictInfo[item.category][item.key] = (item.value, item.comment)

        ctx['dictInfo'] = dict(dictInfo)
        return render(request, 'myadmin/modulemanage/dict/dict.html', ctx)

    def post(self, request):
        try:
            key = request.POST.get('key')
            value = request.POST.get('value')
            category = request.POST.get('category')
            comment = request.POST.get('comment')
            dictItem = Dict(key=key, value=value, category=category, comment=comment)
            dictItem.save()
        except Exception, e:
            return JsonResponse({'msg': '新增失败\n%s' % unicode(e)}, status=500)
        else:
            return JsonResponse({})

    def delete(self, request):
        DELETE = QueryDict(request.body)
        try:
            dict = Dict.objects.get(key=DELETE.get('key'))
        except Dict.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关标签'}, status=404)
        try:
            dict.delete()
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除失败'}, status=500)
        else:
            return JsonResponse({})

    def put(self, request):
        PUT = QueryDict(request.body)
        try:
            item = Dict.objects.get(key=PUT.get('key'))
        except Dict.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关字典项'}, status=404)
        item.value = PUT.get('value')
        item.comment = PUT.get('comment')
        try:
            item.save()
        except Exception, e:
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

            try:
                ctx['autosave_interval'] = Dict.objects.get(key='autosaveInterval').value
            except Exception, e:
                pass

            post_uuid = request.GET.get('pk')
            try:
                post = Post.objects.get(post_uuid=post_uuid)
            except Post.DoesNotExist, e:
                return render(request, 'error.html', {'error_msg': '没有找到相关文章', 'error_title': '发生错误'})

            post.tags = ' '.join([a.name for a in post.tag.all()])
            ctx['post'] = post
            ctx['type'] = 'edit'
            ctx['categoryList'] = Category.objects.all().order_by('name')
            ctx['tagList'] = Tag.objects.all().order_by('name')
            ctx['quickLinks'] = Dict.objects.filter(category='quick_links')
            return render(request, 'blog/new.html', ctx)

        return render(request, 'myadmin/modulemanage/post/view.html', ctx)

    def put(self, request):
        put = QueryDict(request.body)
        act = put.get('act')
        if not act or act not in ('save', 'load', 'clear'):
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
        return JsonResponse({})

    def delete(self, request):
        DELETE = QueryDict(request.body)
        try:
            post = Post.objects.get(post_uuid=DELETE.get('target'))
        except Post.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关文章'}, status=404)
        try:
            post.delete()
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除失败'}, status=500)
        try:  # 和Post关联但是没有反应到模型层中的数据，需要手动额外删除
            # 删除redis中read_count缓存
            back = self.REDIS.hdel(self.READ_COUNT_KEY, post.post_uuid)
            if back is None:
                raise Exception('No such key in redis found: %s' % self.READ_COUNT_KEY + post.post_uuid)

            # 删除文章中上传的图片
            if DELETE.get('del_img') == 'true':
                postImgDir = os.path.join(settings.IMG_UPLOAD_DIR, str(post.post_uuid))
                if os.path.isdir(postImgDir):
                    shutil.rmtree(postImgDir)

        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '文章相关数据删除失败'}, status=501)

        return JsonResponse({})

    def post(self, request):

        try:
            post = Post.objects.get(post_uuid=request.POST.get('post_uuid'))
        except Post.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关文章'}, status=404)

        try:
            post.title = request.POST.get('title')
            post.content = request.POST.get('content')
            post.is_top = request.POST.get('is_top') == 'true'
            post.is_reprint = request.POST.get('is_reprint') == 'true'
            post.reprint_src = request.POST.get('reprint_src')
            post.edit_time = datetime.datetime.now()

            if request.POST.get('is_publish') == 'true':
                post.status = '0'
            else:
                post.status = '1'

            post.abstract = NewPostView.markdown2text(post.content)[:150]  # 这个方法定义在NewPostView里了…
            post.save()

        except Exception, e:
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
                except Tag.DoesNotExist, e:
                    print traceback.format_exc(e)
                    continue
                post.tag.add(tag_obj)
            post.save()
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '关联文章分类/标签失败'}, status=500)

        return JsonResponse({'next': reverse('detail', kwargs={'uuid': post.post_uuid})})


class CommentManage(View):
    def get(self, request):
        ctx = {}
        return render(request, 'myadmin/modulemanage/comment/view.html', ctx)

    def delete(self, request):
        DELETE = QueryDict(request.body)
        try:
            comment = Comment.objects.get(comment_id=DELETE.get('target'))
        except Comment.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关分类'}, status=404)
        try:
            comment.delete()
        except Exception, e:
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
        except Comment.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关留言'}, status=404)
        try:
            message.delete()
        except Exception, e:
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
            except AccessControl.DoesNotExist, e:
                raise Http404

            ctx['ac'] = ac
            return render(request, 'myadmin/modulemanage/accesscontrol/edit.html', ctx)
        elif request.GET.get('type') == 'add':
            return render(request, 'myadmin/modulemanage/accesscontrol/edit.html')

        return render(request, 'myadmin/modulemanage/accesscontrol/view.html', ctx)

    def delete(self, request):
        DELETE = QueryDict(request.body)
        try:
            ac = AccessControl.objects.get(ac_id=DELETE.get('target'))
        except AccessControl.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关权限记录'}, status=404)
        try:
            ac.delete()
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除失败'}, status=500)

        return JsonResponse({})

    def post(self, request):
        try:
            source_ip = request.POST.get('source_ip')
            control_type = request.POST.get('control_type')
            domain = request.POST.get('domain')
            ac = AccessControl(source_ip=source_ip, control_type=control_type, domain=domain)
            ac.save()
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '新增规则失败'}, status=500)
        else:
            return JsonResponse({})

    def put(self, request):
        PUT = QueryDict(request.body)
        try:
            ac_id = PUT.get('ac_id')
            ac = AccessControl.objects.get(ac_id=ac_id)
        except AccessControl.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关的权限控制记录'}, status=404)

        try:
            ac.source_ip = PUT.get('source_ip')
            ac.control_type = PUT.get('control_type')
            ac.domain = PUT.get('domain')
            ac.save()
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '更新权限控制记录失败'}, status=500)

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
        type, filename = fn.split('__', 1)
        if not type or not filename or type not in ('db', 'upload'):
            raise Exception('Invalid request')
    except Exception, e:
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

    redis.set(settings.LAST_BACKUP_KEY, time.time())

    return response


class PaperdbPaperManage(View):

    def get(self, request):
        ctx = {}
        return render(request, 'myadmin/modulemanage/paperdb/paper/view.html', ctx)

    def delete(self, request):
        param = QueryDict(request.body)

        uuid = param.get('target')
        try:
            paper = Paper.objects.get(paper_uuid=uuid)
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return JsonResponse({'msg': '没有发现相关论文记录'}, status=404)

        try:
            references = Reference.objects.filter(Q(reference_src=paper)|Q(reference_trg=paper))
            for ref in references:
                ref.delete()

            paper.comment.delete()
            paper.delete()
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return JsonResponse({'msg': '删除失败'}, status=500)
        else:
            return JsonResponse({})


class PaperdbTagManage(View):

    def get(self, request):
        ctx = {}

        pk = request.GET.get('pk')
        if pk is None:
            return render(request, 'myadmin/modulemanage/paperdb/tag/view.html', ctx)
        elif pk == 'n':
            return render(request, 'myadmin/modulemanage/paperdb/tag/new.html', ctx)
        else:
            try:
                tag = ResearchTag.objects.get(research_tag_id=pk)
            except Exception as e:
                logger.error(traceback.format_exc(e))
                return render(request, 'error.html', {'error_msg': '没有发现相关记录'})
            ctx['tag'] = tag
            return render(request, 'myadmin/modulemanage/paperdb/tag/new.html', ctx)

    def post(self, request):
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        description = request.POST.get('description')
        if pk == 'n':
            new_tag = ResearchTag(name=name, description=description)
            try:
                new_tag.save()
            except Exception as e:
                logger.error(traceback.format_exc(e))
                return JsonResponse({'msg': '保存失败'}, status=500)
            else:
                return JsonResponse({})
        else:
            try:
                tag = ResearchTag(research_tag_id=pk)
            except Exception as e:
                logger.error(traceback.format_exc(e))
                return JsonResponse({'msg': '未找到相关记录'}, status=404)
            tag.name = name
            tag.description = description
            try:
                tag.save()
            except Exception as e:
                logger.error(traceback.format_exc(e))
                return  JsonResponse({'msg': '修改失败'}, status=500)
            else:
                return JsonResponse({})

    def delete(self, request):
        param = QueryDict(request.body)
        pk = param.get('target')

        try:
            tag = ResearchTag.objects.get(research_tag_id=pk)
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return JsonResponse({'msg': '未找到相关记录'}, status=404)

        try:
            tag.delete()
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return JsonResponse({'msg': '删除失败'}, status=500)
        else:
            return JsonResponse({})


class PaperdbAuthorManage(View):

    def get(self, request):
        ctx = {}
        return render(request, 'myadmin/modulemanage/paperdb/author/view.html', ctx)

    def delete(self, request):
        param = QueryDict(request.body)
        pk = param.get('target')

        try:
            author = Author.objects.get(author_id=pk)
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return JsonResponse({'msg': '未找到相关记录'}, status=404)

        try:
            author.delete()
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return JsonResponse({'msg': '删除失败'}, status=500)
        else:
            return JsonResponse({})


class WyzcoupCoupManage(View):
    COUP_STATUS = [
        ('0', '未使用'),
        ('1', '已使用'),
        ('2', '已过期')
    ]

    BG_WIDTH = 1080
    BG_HEIGHT = 1440

    def get(self, request):
        ctx = {}

        if request.GET.get('type') == 'edit':
            coup_uuid = request.GET.get('pk')
            try:
                coup = WyzCoup.objects.get(coup_uuid=coup_uuid)
            except WyzCoup.DoesNotExist as e:
                return render(request, 'error.html', {'err_msg': '没有找到相关分类'})
            else:
                coup.expire_time = coup.expire_time.strftime('%Y-%m-%d') if coup.expire_time else ''
                coup.consume_time = coup.consume_time.strftime('%Y-%m-%d') if coup.consume_time else ''
            ctx['coup'] = coup
            ctx['coup_status'] = self.COUP_STATUS
            return render(request, 'myadmin/modulemanage/wyzcoup/coup/edit.html', ctx)
        elif request.GET.get('type') == 'add':
            return render(request, 'myadmin/modulemanage/wyzcoup/coup/add.html', ctx)
        elif request.GET.get('type') == 'download_qr':    # 下载好人卡二维码图示
            dynamic_host = request.GET.get('dh')
            coup_uuid = request.GET.get('pk')
            bg_dir = os.path.join(settings.STATIC_IMAGE_PATH, 'wyz_coup', 'bg')
            bg = Image.open(os.path.join(bg_dir, random.choice([fn for fn in os.listdir(bg_dir) if fn != 'qr.png'])))
            coup_url = '{}{}?coup_uuid={}'.format(dynamic_host, reverse('wyzcoup.coup'), coup_uuid)
            qr = qrcode.make(coup_url)
            qr_w, qr_h = qr.size
            bg_w, bg_h = self.BG_WIDTH, self.BG_HEIGHT
            margin = (bg_w - qr_w) // 2
            bg.paste(qr, (margin, 200, margin+qr_w, 200+qr_h))

            self._draw_text(bg, coup_uuid, qr.size)

            qr_fn = os.path.join(bg_dir, 'qr.png')
            bg.save(qr_fn)

            def file_iterator(filename, chunk_size=512):
                with open(filename, 'rb') as f:
                    while True:
                        c = f.read(chunk_size)
                        if c:
                            yield c
                        else:
                            break

            response = StreamingHttpResponse(file_iterator(qr_fn))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment; filename="qr.png"'
            return response
        ctx['reverse_coup'] = reverse('wyzcoup.coup')
        return render(request, 'myadmin/modulemanage/wyzcoup/coup/view.html', ctx)

    def post(self, request):
        try:
            coup_title = request.POST.get('coup_title')
            if coup_title == '':
                return JsonResponse({'msg': '标题不能为空'}, status=500)
            coup_content = request.POST.get('coup_content')
            expire_time = request.POST.get('expire_time', None)
            coup = WyzCoup(coup_title=coup_title, coup_content=coup_content, expire_time=expire_time)
            coup.save()
        except Exception as e:
            print(traceback.format_exc(e))
            return JsonResponse({'msg': '新增失败'}, status=500)
        else:
            return JsonResponse({})

    def delete(self, request):
        DELETE = QueryDict(request.body)
        try:
            coup = WyzCoup.objects.get(coup_uuid=DELETE.get('target'))
        except WyzCoup.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关好人卡'}, status=404)
        try:
            coup.delete()
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '删除失败'}, status=500)
        else:
            return JsonResponse({})

    def put(self, request):
        PUT = QueryDict(request.body)
        try:
            coup = WyzCoup.objects.get(coup_uuid=PUT.get('coup_uuid'))
        except WyzCoup.DoesNotExist, e:
            return JsonResponse({'msg': '没有找到相关好人卡'}, status=404)
        try:
            coup.coup_status = PUT.get('coup_status')
            coup.consume_time = PUT.get('consume_time')
            coup.expire_time = PUT.get('expire_time')
            coup.coup_title = PUT.get('coup_title')
            coup.coup_content = PUT.get('coup_content')
            coup.coup_note = PUT.get('coup_note')
            if coup.coup_title == '':
                return JsonResponse({'msg': '标题不能为空'}, status=500)
            if coup.consume_time is not None and coup.coup_status != '1':
                return JsonResponse({'msg': '有使用时间的券必须置状态为已使用'}, status=500)
            if coup.consume_time is None and coup.coup_status == '1':
                return JsonResponse({'msg': '需要明确使用时间'}, status=500)
            coup.save()
        except Exception, e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '更新失败'}, status=500)
        else:
            return JsonResponse({})

    def _draw_text(self, bg, coup_uuid, qr_size):
        '''
        给二维码页面添加文字
        :param bg:
        :param coup_uuid:
        :param qr_size:
        :return:
        '''
        draw = ImageDraw.Draw(bg)
        font_path = os.path.join(settings.BASE_DIR, 'fonts', 'xinyou.ttf')
        appendix_font_path = os.path.join(settings.BASE_DIR, 'fonts', 'xinyou2.ttf')
        static_font = ImageFont.truetype(font_path, 60)
        title_font = ImageFont.truetype(font_path, 54)
        appendix_font = ImageFont.truetype(appendix_font_path, 48)
        try:
            coup = WyzCoup.objects.get(coup_uuid=coup_uuid)
        except WyzCoup.DoesNotExist as e:
            return JsonResponse({'msg': '未发现相关UUID好人卡'}, status=500)

        static_text = '快【长按】图片【保存】到手机'
        title_text = '{}'.format(coup.coup_title)
        expire_time = '永远' if coup.expire_time is None else coup.expire_time.strftime('%Y-%m-%d')
        expire_time = '有效期至【{}】'.format(expire_time)
        appendix_text = '亲我一下可以延期o(*￣︶￣*)o'

        bg_w = self.BG_WIDTH
        bg_h = self.BG_HEIGHT
        qr_w, qr_h = qr_size
        static_text_w, static_text_h = static_font.getsize(static_text)
        draw.text(((bg_w - static_text_w) // 2, (200 - static_text_h) // 2), static_text, font=static_font, fill=(0,0,0))
        title_text_w, title_text_h = title_font.getsize(title_text)
        draw.text(((bg_w - title_text_w) // 2, qr_h+220), title_text, font=title_font, fill=(0,0,0))
        expire_time_w, expire_time_h = title_font.getsize(expire_time)
        draw.text(((bg_w - expire_time_w) // 2, qr_h + 220 + title_text_h + 20), expire_time, font=title_font, fill=(0,0,0))
        if coup.expire_time is not None:
            appendix_text_w, appendix_text_h = appendix_font.getsize(appendix_text)
            draw.text(((bg_w - appendix_text_w) // 2, qr_h + 240 + title_text_h + expire_time_h + 10), appendix_text, font=appendix_font, fill=(0,0,0))