#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
This script is written for update process of FTKBlog.
Please make sure that this script file is placed in the directory [FTKBLOG_ROOT]/scripts.
'''

import logging
import os
import re
import sys
from subprocess import Popen, PIPE

dirname = os.path.dirname
join = os.path.join
BASE_DIR = dirname(dirname(os.path.abspath(__file__)))
PROJECT_ROOT = dirname(BASE_DIR)
BIN_PATH = join(PROJECT_ROOT, 'bin')
ENV_PYTHON = join(PROJECT_ROOT, 'FTKEnv', 'bin', 'python')

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def _check():
    logging.info('Checking active user...')
    p = Popen('whoami', shell=True, stdout=PIPE, stderr=PIPE)
    out,err = p.communicate()
    if out.strip() != 'ftkblog' or err:
        raise Exception('Please update the app with correct user [ftkblog].')

    logging.info('Checking virtual environment...')
    isfile = os.path.isfile
    isdir = os.path.isdir
    if not isfile(ENV_PYTHON):
        # print ENV_PYTHON
        raise Exception('Virtual Environment configuration is incorrect.')

    # not precise check
    logging.info('Checking directory sturcture...')
    if (not isdir(join(BASE_DIR, 'blog'))) or (not isdir(join(BASE_DIR, 'scripts'))) or\
            (not isdir(join(BASE_DIR, 'ftkuser'))) or (not isdir(PROJECT_ROOT)):
        raise Exception('FTKBlog root directory seems abnormal. Please check again if this script is placed in the right place.')

def _stop_app():
    logging.info('Stopping app...')
    stop_bin = join(BIN_PATH, 'stop.sh')
    flag = os.system(stop_bin)
    if flag != 0:
        raise Exception('Error encounter while stopping.')

def _backup_old_app():
    logging.info('Doing backup for old apps...')
    old_old = join(PROJECT_ROOT, 'FTKBlog.old.old')
    old = join(PROJECT_ROOT, 'FTKBlog.old')
    current = BASE_DIR

    flag = os.system('rm -rf {}'.format(old_old))
    if flag != 0:
        raise Exception('Error encounter while deleting .old.old')

    flag = os.system('mv {} {}'.format(old, old_old))
    if flag != 0:
        raise Exception('Error encounter while moving .old to .old.old')

    flag = os.system('mv {} {}'.format(current, old))
    if flag != 0:
        raise Exception('Error encounter while moving current to .old')

def _clone_latest():
    logging.info('Cloning latest app from git...')
    cmd = 'cd {};git clone ssh://git@127.0.0.1:12022/MyGit/FTKBlog.git'.format(PROJECT_ROOT)
    flag = os.system(cmd)
    if flag != 0:
        raise Exception('Error encounter while git cloning latest version.')

def _reconfig():
    logging.info('Re-congifuring app...')
    config_file = join(BASE_DIR, 'FTKBlog', 'settings.py')
    f = open(config_file, 'r')
    line = f.readline()
    new_lines = []
    while line:
        if line.strip().startswith('#'):
            pass
        elif re.match('(.*?)DEBUG ?= ?True(.*)$', line):
            m = re.match('(.*?)DEBUG ?= ?True(.*)$', line)
            line = '{}DEBUG = False{}\n'.format(m.group(1), m.group(2))
        elif re.match('(.*?)redis\:\/\/[\d\.]+?\:6379\/(\d+)(.+)$', line):
            m = re.match('(.+?)redis\:\/\/[\d\.]+?\:6379\/(\d+)(.+)$', line)
            line = '{}redis://127.0.0.1:6379/{}{}\n'.format(m.group(1), m.group(2), m.group(3))
        elif re.match('(.*?)[\d\.]+\:9200(.*?)$', line):
            m = re.match('(.*?)[\d\.]+\:9200(.*?)$', line)
            line = '{}127.0.0.1:9200{}\n'.format(m.group(1), m.group(2))
        new_lines.append(line)
        line = f.readline()

    f.close()
    logging.info('Writing into new configuration file...')
    f = open(config_file, 'w')
    f.writelines(new_lines)
    f.close()

def _copy_online_files():
    apps = ['blog', 'ftkuser']
    old = join(PROJECT_ROOT, 'FTKBlog.old')
    current = BASE_DIR
    logging.info('Copying online files(migrations) to current app...')
    for app in apps:
        cmd = 'rm -f {}/*'.format(join(BASE_DIR, app, 'migrations'))
        flag = os.system(cmd)
        if flag != 0:
            raise Exception('Error encounter while removing migrations files of app:{}'.format(app))
        cmd = 'cp -f {}/* {}'.format(join(old, app, 'migrations'), join(current, app, 'migrations'))
        flag = os.system(cmd)
        if flag != 0:
            raise Exception('Error encounter while copying old migrations files of app:{}'.format(app))

    logging.info('Copying online files(uploads) to current app...')
    cmd = 'cp -rf {} {}'.format(join(old, 'static', 'upload'), join(current, 'static'))
    flag = os.system(cmd)
    if flag != 0:
         raise Exception('Error encounter while copying old static-upload files.')

def _manage_work():
    logging.info('Checking for migrations on current app...')
    cmd = '{} {} showmigrations'.format(ENV_PYTHON, join(BASE_DIR, 'manage.py'))
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out,err = p.communicate()
    if out.find('[ ]') != -1:
        print '=' * 20
        print 'Some migrations not done yet.\nPlease do it manually.'
        print '=' * 20
        print out
        print err
        sys.exit(1)
    else:
        print out
        print err

    logging.info('Updating crontab jobs...')
    cmd = '{} {} crontab add'.format(ENV_PYTHON, join(BASE_DIR, 'manage.py'))
    flag = os.system(cmd)
    if flag != 0:
        raise Exception('Error encounter while adding new crontab for django.')

def _start_app():
    logging.info('Starting app now...')
    start_bin = join(BIN_PATH, 'start.sh')
    flag = os.system(start_bin)
    if flag != 0:
        raise Exception('Error encounter while starting new app.')

def main():
    # 变更前检查
    _check()
    # 停止应用
    _stop_app()
    # 备份旧应用
    _backup_old_app()
    # 从git上clone新应用
    _clone_latest()
    # 配置重写
    _reconfig()
    # 从旧应用复制必要的线上文件
    _copy_online_files()
    # manage.py相关工作
    _manage_work()
    # 启动应用
    _start_app()

if __name__ == '__main__':
    main()
    logging.info('All update is done.')
