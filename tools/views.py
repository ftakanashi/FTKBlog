# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from ratelimit.decorators import ratelimit

import logging
import paramiko
import traceback

logger = logging.getLogger('django')

# Create your views here.

def get_proxy_ssh_client():
    '''
    获取proxy工作服务器的ssh客户端
    '''
    proxy_config = settings.TOOLS_CONFIG['proxy']
    host = proxy_config.get('proxy_name')
    user = proxy_config.get('proxy_user')
    port = proxy_config.get('proxy_port')
    pkey = proxy_config.get('proxy_pkey')
    try:
        key = paramiko.RSAKey.from_private_key(pkey)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, username=user, port=port, pkey=key)
    except Exception as e:
        logger.warning('获取远端工作节点ssh客户端失败')
        logger.warning(traceback.format_exc(e))
        return None
    else:
        return ssh

def close_proxy_ssh_client(ssh):
    try:
        ssh.close()
    except Exception as e:
        return False
    else:
        return True

class BiologyRhythmView(View):

    @ratelimit(key='ip', rate='1/1s')
    def get(self, request):

        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

        ctx = {}
        return render(request, 'tools/biorhy.html', ctx)

class PNHBDownloadView(View):
    @ratelimit(key='ip', rate='1/1s')
    def get(self, request):

        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

        ctx = {}
        return render(request, 'tools/pnhb.html', ctx)

    @ratelimit(key='ip', rate='1/5s', block=True)
    def post(self, request):
        url = request.POST.get('url')
        filename = request.POST.get('filename')
        logger.info('神秘链接请求URL[{}]    文件名[{}]'.format(url, filename))
        ssh = get_proxy_ssh_client()
        if ssh is None:
            return JsonResponse({'msg': '获取远程工作节点客户端失败┭┮﹏┭┮'},status=500)
        script = settings.TOOLS_CONFIG['pnhb']
        cmd = '{} -url {}'.format(script, url)
        if filename != '':
            cmd += ' -filename {}'.format(filename)
        stdin,stdout,stderr = ssh.exec_command(cmd)
        out,err = stdout.read(), stderr.read()
        close_proxy_ssh_client(ssh)
        if err or out.strip() != '0':
            logger.warning('下载节点远程stderr: {}'.format(err))
            logger.warning('下载节点远程stdout: {}'.format(out))
            return JsonResponse({'msg': '远程下载节点报错了┭┮﹏┭┮'})
        if out.strip() == '0':
            return JsonResponse({'msg': '下载命令已经顺利发出ヾ(◍°∇°◍)ﾉﾞ'})
