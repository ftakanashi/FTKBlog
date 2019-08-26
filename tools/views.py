# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.http import JsonResponse, QueryDict
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
from django_redis import get_redis_connection

import datetime
import json
import logging
import os
import paramiko
import requests
import subprocess
import traceback
import uuid

from tasks import you_get
from utils import HJDictQuery, RateQuery

logger = logging.getLogger('django')

redis = get_redis_connection()


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
        key = paramiko.RSAKey.from_private_key_file(pkey)
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
        ctx['year_opt'] = range(1970, 2031)
        ctx['month_opt'] = range(1, 13)
        ctx['day_opt'] = range(1, 32)
        ctx['today'] = datetime.datetime.today()
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

        try:
            script = settings.TOOLS_CONFIG['pnhb']['script_path']
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return JsonResponse({'msg': '获取远程工作节点工作脚本目录失败'}, status=500)

        ssh = get_proxy_ssh_client()
        if ssh is None:
            return JsonResponse({'msg': '获取远程工作节点客户端失败┭┮﹏┭┮'}, status=500)

        cmd = '{} -url {}'.format(script, url)
        if filename != '':
            cmd += ' -filename {}'.format(filename)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out, err = stdout.read(), stderr.read()
        close_proxy_ssh_client(ssh)
        if err or out.strip() != '0':
            logger.warning('下载节点远程stderr: {}'.format(err))
            logger.warning('下载节点远程stdout: {}'.format(out))
            return JsonResponse({'msg': '远程下载节点报错了┭┮﹏┭┮<br>详情见后台日志'})
        if out.strip() == '0':
            return JsonResponse({'msg': '下载命令已经顺利发出ヾ(◍°∇°◍)ﾉﾞ'})


class YouGetDownloadView(View):
    YOU_GET_CACHE_KEY = settings.TOOLS_CONFIG['you-get']['cache_key']
    YOU_GET_CACHE_TTL = settings.TOOLS_CONFIG['you-get']['cache_ttl']
    YOU_GET_DEFAULT_DOWNLOAD_PATH = settings.TOOLS_CONFIG['you-get']['default_download_path']
    YOU_GET_MONITOR_API = settings.CELERY_FLOWER_API

    @ratelimit(key='ip', rate='1/s')
    def get(self, request):

        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

        ctx = {}
        ctx['messages'] = []
        if request.GET.get('ssp') == '1':  # support site
            return render(request, 'tools/you-get/supportSiteTable.html', ctx)
        elif request.GET.get('tm') == '1':  # task monitor
            api_url = self.YOU_GET_MONITOR_API + 'tasks'
            try:
                task_info = json.loads(requests.get(api_url).content)
            except Exception as e:
                return render(request, 'error.html', {'error_msg': '获取任务信息失败'})
            res = []
            for task in task_info.values():
                tmp = {}
                if not task['name'].endswith('you_get'):
                    continue
                tmp['uuid'] = task['uuid']
                kwargs_info = eval(task['kwargs'])
                tmp.update(kwargs_info)
                tmp['state'] = task['state']
                tmp['started'] = task['started']
                tmp['runtime'] = task['runtime']
                res.append(tmp)

            res = json.dumps(res, encoding='utf-8')
            ctx['task_info'] = res
            return render(request, 'tools/you-get/taskMonitor.html', ctx)

        if request.GET.get('u') is None:
            return render(request, 'tools/you-get/analyze.html', ctx)
        else:
            uuid = request.GET.get('u')
            # content = redis.get(self.YOU_GET_CACHE_KEY.format(uuid))
            contents = []
            key = self.YOU_GET_CACHE_KEY.format(uuid)
            if not redis.exists(key):
                ctx['messages'].append('没有找到相关缓存。关联键:{}'.format(uuid))
                return render(request, 'tools/you-get/analyze.html', ctx)
            while redis.llen(key) > 0:
                contents.append(redis.lpop(key))

            ctx['content'] = '###'.join(contents)
            ctx['is_playlist'] = len(contents) > 1
            ctx['uuid'] = uuid

            return render(request, 'tools/you-get/download.html', ctx)

    @ratelimit(key='ip', rate='1/1s', block=True)
    def post(self, request):
        method = request.POST.get('method', 'analyze')
        if method not in ('analyze', 'download'):
            return JsonResponse({'msg': '错误的请求类型'}, status=500)

        if method == 'analyze':
            url = request.POST.get('url')
            if not url:
                return JsonResponse({'msg': '错误的url'}, status=500)

            do_playlist = request.POST.get('playlist') == '1'
            cmd = 'you-get --json'
            if do_playlist:
                cmd += ' --playlist'
            cmd += ' {}'.format(url)
            logger.info('You-Get下载分析链接：[{}]'.format(cmd))
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()

            if err and err.find('This is a multipart video') == -1:
                logger.error('You-Get分析失败：\n{}'.format(err))
                return JsonResponse({'msg': '分析链接失败'}, status=404)

            out = '}\n' + out + '{'
            out_strs = ['{' + f + '}' for f in out.strip('}\n{').split('}\n{')]

            try:
                for out_str in out_strs:
                    json.loads(out_str)
            except Exception as e:
                logger.error('[{}]解析JSON格式失败：{}'.format(out_str, traceback.format_exc(e)))
                return JsonResponse({'msg': '分析内容格式有误，解析失败'}, status=500)
            else:
                u = str(uuid.uuid4())
                key = self.YOU_GET_CACHE_KEY.format(u)
                for out_str in out_strs:
                    redis.rpush(key, out_str)
                redis.expire(key, self.YOU_GET_CACHE_TTL)
                return JsonResponse({'uuid': u})
        elif method == 'download':

            def check_safety(fn):
                for char in '~!@#$%^&*()_+`\';:\"<>,/?{} ':
                    if char in fn:
                        return False
                return True

            list_download = request.POST.get('l') == 'true'
            form = request.POST.get('f')
            with_caption = request.POST.get('c') == 'true'
            url = request.POST.get('u')
            if not list_download:
                output_filename = request.POST.get('o', '')
                if not check_safety(output_filename):
                    return JsonResponse({'msg': '输入的文件名有潜在危险性'}, status=500)
            else:
                output_filename = None

            default_path = self.YOU_GET_DEFAULT_DOWNLOAD_PATH
            r = you_get.delay(url=url,
                              form=form,
                              with_caption=with_caption,
                              default_path=default_path,
                              output_fn=output_filename,
                              list_download=list_download)
            return JsonResponse({'msg': '远程下载命令已成功发出(〃\'▽\'〃)'})

    @ratelimit(key='ip', rate='1/1s', block=True)
    def delete(self, request):
        DELETE = QueryDict(request.body)
        uuid = DELETE.get('u')
        api_url = self.YOU_GET_MONITOR_API + 'task/revoke/{}'.format(uuid)
        logger.info('发起停止任务请求:[{}]'.format(api_url))
        try:
            res = request.post(api_url, data={'terminate': True})
            if res.status_code != 200:
                raise Exception(res.content)
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return JsonResponse({'msg': '停止任务失败'}, status=500)
        else:
            return JsonResponse({'msg': json.loads(res.content)['message']})


class SSRConfigView(View):
    @ratelimit(key='ip', rate='1/1s')
    def get(self, request):

        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

        ctx = {}
        try:
            show_port = settings.TOOLS_CONFIG['ssr_config']['show_port_path']
            # config = settings.TOOLS_CONFIG['ssr_config']['config_path']
        except Exception as e:
            return render(request, 'error.html', {'error_msg': '获取远程工作节点脚本目录失败'})

        ssh = get_proxy_ssh_client()
        if ssh is None:
            return render(request, 'error.html', {'error_msg': '获取远程工作节点客户端失败┭┮﹏┭┮'})

        stdin, stdout, stderr = ssh.exec_command(show_port)
        out, err = stdout.read(), stderr.read()
        close_proxy_ssh_client(ssh)
        if err:
            logger.error('获取远程SSR端口失败:\n{}'.format(err))
            ctx['ssr_ports'] = ['获取当前端口失败', ]
        else:
            ctx['ssr_ports'] = out.strip().split(',')

        return render(request, 'tools/ssr.html', ctx)

    @ratelimit(key='ip', rate='1/5s', block=True)
    @method_decorator(login_required)
    def post(self, request):
        info_str = request.POST.get('info')
        infos = info_str.split(',')
        ports, blacklists = [], []
        for info in infos:
            port, blacklist = info.split(':')
            ports.append(port)
            blacklists.append(blacklist)

        try:
            config = settings.TOOLS_CONFIG['ssr_config']['do_config_path']
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return JsonResponse({'msg': '获取远程工作节点脚本目录失败'}, status=500)

        cmd = config
        cmd += ' -ports {}'.format(','.join(ports))
        cmd += ' -blacklist {}'.format(''.join(blacklists))
        logger.info('本次执行命令 [{}]'.format(cmd))

        ssh = get_proxy_ssh_client()
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out, err = stdout.read(), stderr.read()
        close_proxy_ssh_client(ssh)

        if err:
            logger.error('修改SSR远程端口失败:{}'.format(err))
            return JsonResponse({'msg': '远程修改端口过程报错了┭┮﹏┭┮<br>详情见后台日志'})
        else:
            logger.info('修改SSR远程端口为{}'.format(out.strip()))
            return JsonResponse({'msg': '远程端口已经修改为<h1 style="color: red;">{}</h1>'.format(out.strip())})


class SiteDictView(View):
    def get(self, request):
        ctx = {}
        config = settings.TOOLS_CONFIG['site_dict']
        ctx.update(config)

        return render(request, 'tools/sitedict.html', ctx)

    @ratelimit(key='ip', rate='1/1s', block=True)
    def post(self, request):
        word = request.POST.get('w')
        trans_type = request.POST.get('t')

        config = settings.TOOLS_CONFIG.get('site_dict')
        if type(config) is not dict:
            logger.error('读取配置失败。可能是因为没有配置TOOLS_CONFIG或没在TOOLS_CONFIG中配置site_dict')
            return JsonResponse({'msg': '查询失败'}, status=500)

        if not word or not trans_type:
            logger.error('错误的参数[word={}, trans_type={}]'.format(word, trans_type))
            return JsonResponse({'msg': '错误的参数！'}, status=500)

        if trans_type not in config.get('valid_lang_pair'):
            logger.error('不支持的语对:{}'.format(trans_type))
            return JsonResponse({'msg': '目前还不支持此类语言查询'}, status=500)

        root_url = settings.TOOLS_CONFIG.get('site_dict').get('root_url')
        hj_dict = HJDictQuery(root_url)

        try:
            res = hj_dict.query(word, trans_type)
        except Exception as e:
            logger.error('请求失败：\n{}'.format(traceback.format_exc(e)))
            return JsonResponse({'msg': '查询失败'}, status=500)
        else:
            if res is None:
                logger.info('未在远端找到和[{}]相关的词'.format(word))
                return JsonResponse({'msg': '远端未能找到相关词'}, status=404)
            logger.info('找到[{}]个相关的词：{}'.format(len(res), [w.get('header_word') for w in res]))
            return JsonResponse({'res': res})


class RateToolView(View):
    RATE_CACHE_KEY = settings.TOOLS_CONFIG['rate_tool']['redis_key']

    @ratelimit(key='ip', rate='1/1s')
    def get(self, request):

        if getattr(request, 'limited', False):
            return render(request, 'error.html', {'error_msg': '你点得太急了 稍微过一会儿再试吧Σ(っ °Д °;)っ', 'error_title': ''})

        ctx = {}
        cache = redis.get(self.RATE_CACHE_KEY)
        if cache is None:
            root_url = settings.TOOLS_CONFIG['rate_tool']['root_url']
            rate_query = RateQuery(root_url)
            info = rate_query.query()
            if len(info) == 0:
                ctx['error_msg'] = '建议你去百度一下哦'
                ctx['error_title'] = '获取汇率信息失败了(ΩДΩ)'
                return render(request, 'error.html', ctx)
            else:
                update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = {'data': info, 'update_time': update_time}
                redis.set(self.RATE_CACHE_KEY, json.dumps(data))
        else:
            data = json.loads(cache)
            info = data['data']
            update_time = data['update_time']

        ctx['currs'] = [i['currency'] for i in info]
        ctx['last_update'] = update_time
        return render(request, 'tools/ratetool.html', ctx)

    @ratelimit(key='ip', rate='1/1s', block=True)
    def post(self, request):
        credit_value = request.POST.get('v')
        src_currency = request.POST.get('s')
        trg_currency = request.POST.get('t')
        update_rate = request.POST.get('u') == 'true'

        logger.info('汇率计算请求：源币[{}]  目标币[{}]  金额[{}]  强制更新汇率[{}]'.format(
                src_currency, trg_currency, credit_value, update_rate
        ))
        cache = redis.get(self.RATE_CACHE_KEY)
        if update_rate or cache is None:
            root_url = settings.TOOLS_CONFIG['rate_tool']['root_url']
            rate_query = RateQuery(root_url)
            info = rate_query.query()
            if len(info) == 0:
                return JsonResponse({'msg': '获取汇率信息失败(ΩДΩ)'}, status=500)
            else:
                update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = {'data': info, 'update_time': update_time}
                redis.set(self.RATE_CACHE_KEY, json.dumps(data))
        else:
            info = json.loads(cache)['data']

        src_rate = trg_rate = None
        src_alias = trg_alias = ''
        for _info in info:
            if _info['currency'] == src_currency:
                src_rate = float(_info['refePrice'])
                src_alias = _info['currency']
            elif _info['currency'] == trg_currency:
                trg_rate = float(_info['refePrice'])
                trg_alias = _info['currency']

        if src_rate is None:
            logger.error('错误的货币类型[{}]'.format(src_rate))
            return JsonResponse({'msg': '不支持该源币种'}, status=500)
        elif trg_rate is None:
            logger.error('错误的货币类型[{}]'.format(trg_rate))
            return JsonResponse({'msg': '不支持该目标币种'}, status=500)
        else:
            logger.info('100外币兑换人民币汇率 = [{}:{}], [{}:{}]'.format(
                    src_currency, src_rate, trg_currency, trg_rate
            ))

        credit_value = round(float(credit_value), 4)
        rmb_value = (credit_value / 100.0) * src_rate
        trg_value = (rmb_value / trg_rate) * 100.0
        direct_rate = 100 * src_rate / trg_rate
        trg_value = round(trg_value, 4)
        direct_rate = round(direct_rate, 4)

        logger.info('[{}] {} 兑换 [{}] {}\n中间价RMB {}\n直接汇率 {}'.format(
                credit_value, src_alias, trg_value, trg_alias, rmb_value, direct_rate
        ))

        return JsonResponse({'credit': trg_value, 'rate': direct_rate})
