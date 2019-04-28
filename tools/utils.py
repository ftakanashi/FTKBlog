# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
import logging
import re
import requests
import sys
import traceback

from celery.task import Task

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger('django')

class HJDictException(Exception):
    pass

class HJDictQuery(object):
    def __init__(self, root_url):
        self.root_url = root_url
        self._header = {
            'Host': 'dict.hjenglish.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://dict.hjenglish.com/jp/',
            'Connection': 'keep-alive',
            'Cookie': 'TRACKSITEMAP=3%2C6%2C11%2C19%2C20%2C22%2C23%2C; _REF=https://www.baidu.com/link?url%3DkHLD-dJ-56nZQrxUm1PaY56EaoMvrsarMopSHbqtcjqzMysUF3_cyLBK0fq9EsInAIUPeFcJomw0vUySZrEPFK&wd%3D&eqid%3Dc8cc777d0002819c000000045ba9f46e; HJ_UID=71b8e75f-5e84-4210-9e83-079c16b52c66; _SREF_3=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3Dv64RkP1pGjXHb47MtqtHwlGfNT0GzymgGFusRW8_ffKURlzwou-W4gy4f__RellKy4qCq-lTXYrfUGRdqVtUYq%26wd%3D%26eqid%3D92e8c16e00001ecc0000000459fc1c92; hjd_ajax_Language2011=jp; Hm_lvt_d4f3d19993ee3fa579a64f42d860c2a7=1551681508; _SREF_3=https://www.baidu.com/link?url%3Dv64RkP1pGjXHb47MtqtHwlGfNT0GzymgGFusRW8_ffKURlzwou-W4gy4f__RellKy4qCq-lTXYrfUGRdqVtUYq&wd%3D&eqid%3D92e8c16e00001ecc0000000459fc1c92; _SREF_20=https://www.baidu.com/link?url%3D8n7LUmxko-AMn6HKYNkg5OmznZGs3GgR8Jzqr_ZiYHjO3yJQnUV30FAnG7I9I6nPGBRWYEg-fdzLiIeizqnb9_&wd%3D&eqid%3Dcbedd6ff00055657000000045bc68804; _REG=www.baidu.com|; _SREG_3=www.baidu.com|; _UZT_USER_SET_106_0_DEFAULT=2|f2b4e91ce34a632fac0ef544232ddc13; _SREG_20=www.baidu.com|; HJ_SID=4d5e63d4-c595-4109-952a-ae0efd6bb5aa; HJ_SSID_3=22bcedd8-d184-4951-8836-da450039ba98; HJ_CST=0; HJ_CSST_3=0',
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }

    def query(self, word, trans_type):
        if trans_type in ('jc', 'cj'):
            self.root_url += '/jp'
        elif trans_type in ('ce', 'ec'):
            trans_type = 'w'
        self.root_url += '/{}/{}'
        url = self.root_url.format(trans_type, word)
        logger.info('查询词：{}    查询类型：{}    请求到{}'.format(word, trans_type, url))
        try:
            res = requests.get(url, headers=self._header)
            if res.status_code != 200:
                raise HJDictException('HTTP Error [{}]'.format(res.status_code))
        except Exception as e:
            logger.error('获取沪江小D页面信息失败:\n{}'.format(traceback.format_exc(e)))
            raise HJDictException(e)

        soup = BeautifulSoup(res.content, 'html5lib')

        not_found = soup.find(attrs={'class': 'word-notfound'})
        if not_found is not None:
            return None

        # word_infos = soup.find_all(attrs={'class': 'word-details-pane-header'})
        word_infos = soup.select('.word-details-pane')
        if len(word_infos) == 0:
            logger.debug(soup)
            raise HJDictException('Still got none dictionary info from page.')

        res_container = []
        for word_info in word_infos:
            res_info = {}
            header = word_info.find(attrs={'class': 'word-details-pane-header'})
            self.extract('header', header, res_info)
            content = word_info.find(attrs={'class': 'word-details-item-content'})
            if content is None:    # none content is possible
                res_info['detailed_explanation'] = ''
                res_info['detailed_examples'] = []
            else:
                self.extract('content', content, res_info)
            res_container.append(res_info)

        return res_container

    def extract(self, part, obj, container):
        if part == 'header':
            self._extract_header(obj, container)
        elif part == 'content':
            self._extract_content(obj, container)

    def _extract_header(self, header, res):
        res['header_word'] = ''.join(header.find(attrs={'class': 'word-text'}).stripped_strings)
        res['header_pron'] = ''.join(header.find(attrs={'class': 'pronounces'}).stripped_strings)
        audio_info = header.find(attrs={'class': 'word-audio'})
        if audio_info is not None:
            res['header_audio'] = audio_info.attrs.get('data-src')
        else:
            res['header_audio'] = None
        res['meaning'] = re.sub('[\n ]+', '<br>', ''.join(header.find(attrs={'class': 'simple'}).strings).strip())

    def _extract_content(self, content, res):
        section = content.find(attrs={'class': 'detail-groups'})
        pos = ''.join(section.find('dt').stripped_strings)
        dds = []
        for dd in section.select('dd'):
            dd_info = self._extract_one_dd(dd)
            dds.append(dd_info)
        res['detailed_explanation'] = pos
        res['detailed_examples'] = dds

    def _extract_one_dd(self, dd):
        detailed_meaning = ''.join(dd.find('h3').stripped_strings)
        examples = []
        for li in dd.find_all('li'):
            examples.append('&nbsp;&nbsp;/&nbsp;&nbsp;'.join(li.stripped_strings))
        return {'detailed_meaning': detailed_meaning, 'examples': examples}

class RateException(Exception):
    pass

class RateQuery(object):
    def __init__(self, root_url):
        self.root_url = root_url
        self.headers = {
            'Host': 'data.bank.hexun.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }

    def query(self):
        try:
            res = requests.get(self.root_url, headers=self.headers)
            if res.status_code != 200:
                raise RateException('HTTP Error [{}]'.format(res.status_code))
        except Exception as e:
            logger.error('请求汇率页面失败:\n{}'.format(traceback.format_exc(e)))
            return []

        try:
            content = res.content.decode('gbk')
        except UnicodeDecodeError as e:
            logger.warning('用GBK解码失败。使用原文')
            content = res.content

        try:
            raw_match = re.search('PereMoreData\(\[(.+?)\]\)$', content)
            raw = raw_match.group(1)
            info = [{item.split(':')[0]: item.split(':')[1][1:-1].strip() for item in s.strip('{').strip('}').split(',')}
                    for s in raw.split('},{')]
        except Exception as e:
            logger.error('解析汇率数据失败。源数据是\n{}'.format(content))
            logger.error(traceback.format_exc(e))
            return []
        else:
            return info
