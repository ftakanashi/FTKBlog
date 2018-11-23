# -*- coding:utf-8 -*-

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6gz5nmsl-kdkne+(em)uv03^v9_^d(!1#bb8dfj!u+uem)k_19'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pure_pagination',
    'django_elasticsearch_dsl',
    'django_redis',
    'django_crontab',
    'ratelimit',
    'rest_framework',
    'django_filters',
    'blog.apps.BlogConfig',
    'ftkuser.apps.FtkuserConfig',
    'search.apps.SearchConfig',
    'myadmin.apps.MyadminConfig'
]

MIDDLEWARE = [
    'ftkmiddleware.accesscontrol.AccessControlMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'FTKBlog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'FTKBlog.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'db', 'db.sqlite3'),
    }
}

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': '192.168.178.59:9200'
        # 'hosts': '127.0.0.1:9200'
        # 'hosts': '10.13.114.112:9200'
    },
}
ELASTICSEARCH_INDEX = 'ftkblog'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://192.168.178.59:6379/1',
        # 'LOCATION': 'redis://127.0.0.1:6379/1',
        # 'LOCATION': 'redis://10.13.114.112:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 100},
            'PASSWORD': 'franknihao'
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_AGE = 43200
SESSION_CACHE_ALIAS = 'default'

# Logging Configuration
from logconf import *

LOGGING = {
    'version': 1,
    'disable_existing_logger': True,
    'formatters': {
        'standard': STANDARD_FORMATTER
    },
    'handlers': {
        'null': {'level': 'DEBUG','class': 'logging.NullHandler'},
        'root': {'level': 'INFO', 'class': 'logging.handlers.RotatingFileHandler', 'filename': os.path.join(PROJECT_ROOT, 'logs','django.log'),
                 'maxBytes': 1024*1024*10, 'backupCount': 5, 'formatter': 'standard'},
        'cron': dict(filename=os.path.join(PROJECT_ROOT, 'logs', 'cron', 'cron.log'),**STANDARD_ROTATE_HANDLER),
        'elasticsearch': dict(filename=os.path.join(PROJECT_ROOT, 'logs', 'elasticsearch.log'), **STANDARD_ROTATE_HANDLER)
    },
    'loggers': {
        'django':{
            'handlers': ['root'],
            'level': 'INFO'
        },
        'django_crontab.crontab': {
            'handlers': ['cron'],
            'level': 'INFO'
        },
        'django.ftkblog.cron': {
            'handlers': ['cron'],
            'level': 'INFO',
            'propagate': True
        },
        'elasticsearch': {
            'handlers': ['elasticsearch'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# API Restframework configuration
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

# ratelimit configuration
# RATELIMIT_USE_CACHE = 'default'


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CRONLOG = os.path.join(BASE_DIR, 'logs', 'cron', 'cron.log')
CRONJOBS = [
    ('0 */4 * * *', 'blog.cron.sync_read_count'),  # 每隔四小时同步redis中阅读数到库中
    ('0 0 * * *', 'blog.cron.refresh_today_access_count'),  # 每天零时重置当天访问人数
    ('0 0 */2 * *', 'blog.cron.gc_post_image'),  # 每两天清理一次无用的图片
    ('40 9 * * *', 'FTKBlog.cron.db_backup'),  # 每天备份数据库数据
    ('0 1 * * *', 'FTKBlog.cron.upload_backup'),  # 每天备份上传（图片）数据
    ('0 2 */3 * *', 'FTKBlog.cron.migration_backup')  # 每天备份migration记录
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'run')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# File upload setting
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 5

# Pagination settings for pure_pagination
PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 10,
    'MARGIN_PAGES_DISPLAYED': 2,
    'SHOW_FIRST_PAGE_WHEN_INVALID': True
}

######## 一些自定义的配置 ########

# ElasticSearch相关配置
from elasticsearch import Elasticsearch
es_host,es_port = ELASTICSEARCH_DSL.get('default').get('hosts').split(':')
ES_CLIENT = Elasticsearch([
    {'host': es_host, 'port': es_port}
])

# Redis中key的一些配置
READ_COUNT_KEY = 'blog:read_count'
ACCESS_COUNT_KEY = 'blog:access_count'
CACHE_KEY = 'blog:post_cache'
UNREAD_COMMENTS_KEY = 'blog:unread_comment_queue'
UNREAD_MESSAGE_KEY = 'blog:unread_message_queue'
VERI_CODE_KEY = 'blog:veri_code:%s'

# post中图片上传目录
IMG_UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'upload', 'post-image')

# 自动备份周期（天）
BACKUP_PERIOD = 30

######## 自定义初始化 ##########
from scripts import *
redis_init()
# todo editormd的onpaste自动黏贴图片
'''
似乎django有个自动压缩前端所有需要比如css，js这些文件的组件
'''