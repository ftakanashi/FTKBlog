# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect,reverse
from django.http.response import Http404
from django.views.generic import View
from pure_pagination import Paginator
from .models import Post, Category, Tag
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

        posts = posts.order_by('update_time').reverse()
        p = Paginator(posts, 2, request=request)
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