# -*- coding:utf-8 -*-

'''
本脚本主要用于上线后生产和开发文件的替换。
1. 将原生产各个app下migrations中的migrations文件替换到新生产目录，即本目录中
2. 将原生产/static/upload替换到新生产/static/upload
'''

from __future__ import unicode_literals
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
FTK_HOME = '/home/ftkblog/FrankTakanashiKazuyaBlog'

def replace_migration():
    pass

if __name__ == '__main__':
    old_dir = raw_input('你刚刚重命名过的，原部署目录是:%s' % FTK_HOME)
    if old_dir == '':
        old_dir = 'FTKBlog.old'
    old_dir = os.path.join(FTK_HOME,old_dir)


