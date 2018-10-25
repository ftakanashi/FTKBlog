# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect,reverse
from django.http.response import Http404
from django.views.generic import View
from pure_pagination import Paginator
from .models import Post
# Create your views here.

class IndexView(View):
    def get(self, request):
        try:
            page = int(request.GET.get('page','1'))
        except Exception,e:
            page = 1
        posts = Post.objects.filter(status=0).order_by('update_time').reverse()
        p = Paginator(posts, 2, request=request)
        paged_posts = p.page(page)
        ctx = {}
        ctx['posts'] = paged_posts
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