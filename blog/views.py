# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect,reverse
from django.http.response import Http404, JsonResponse
from django.views.generic import View
from pure_pagination import Paginator
from .models import Post, Category, Tag

import json
import re
import traceback
# Create your views here.

class IndexView(View):
    def get(self, request):
        try:
            page = int(request.GET.get('page','1'))
        except Exception,e:
            page = 1

        sCate = request.GET.get('category')
        if sCate is not None:
            posts = Post.objects.filter(category__cate_id=sCate).filter(status=0)
        else:
            posts = Post.objects.filter(status=0)

        posts = posts.order_by('-is_top','-update_time')
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

    @classmethod
    def markdown2text(cls, markdown):
        p = re.compile('[\\\_\[\]\#\+\!]|[\`\*\-]{3,}|^>')
        return p.sub('', markdown)

    def get(self, request):
        categoryList = Category.objects.all()
        tagList = Tag.objects.all()
        return render(request, 'blog/new.html', locals())

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
        except Exception,e:
            print traceback.format_exc(e)
            return JsonResponse({'msg': '上传内容错误'},status=500)

        processFlag = False
        try:
            post = Post(**postInfo)
            post.save()
            processFlag = True
            for tag in tags:
                if isinstance(tag,unicode):
                    tag = int(tag)
                post.tag.add(Tag.objects.get(tag_id=tag))
        except Exception,e:
            print traceback.format_exc(e)
            if processFlag:
                postUrl = reverse('detail',kwargs={'uuid': post.post_uuid})
                return JsonResponse({'msg': '添加文章成功，但是关联标签失败','next': postUrl})
            else:
                return JsonResponse({'msg': '添加文章失败'},status=500)
        else:
            postUrl = reverse('detail',kwargs={'uuid': post.post_uuid})
            return JsonResponse({'next': postUrl})



class PostView(View):
    def get(self, request, uuid):
        ctx = {}
        try:
            postId = int(uuid)
            url = reverse('detail',kwargs={'uuid':unicode(Post.objects.get(post_id=postId).post_uuid)})
            return redirect(url)
        except ValueError,e:
            pass

        try:
            post = Post.objects.get(post_uuid=uuid)
        except Post.DoesNotExist,e:
            return Http404()
        else:
            ctx['post'] = post

        return render(request, 'blog/post.html', ctx)
