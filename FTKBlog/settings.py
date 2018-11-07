# -*- coding:utf-8 -*-

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': '192.168.178.59:9200'
    },
}
ELASTICSEARCH_INDEX = 'ftkblog'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://192.168.178.59:6379/1',
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

CRONJOBS = [
    ('*/1 * * * *', 'blog.cron.sync_read_count','>> %s' % os.path.join(BASE_DIR,'logs','cron','sync_read_count.log')),
    ('0 0 0 * *', 'blog.cron.refresh_today_access_count', '>> %s' % os.path.join(BASE_DIR,'logs','cron','refresh_today_access_count.log'))
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
    os.path.join(BASE_DIR, 'upload')
]

PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 10,
    'MARGIN_PAGES_DISPLAYED': 2,
    'SHOW_FIRST_PAGE_WHEN_INVALID': True
}

######## 一些自定义的配置 ########
from elasticsearch import Elasticsearch
es_host,es_port = ELASTICSEARCH_DSL.get('default').get('hosts').split(':')
ES_CLIENT = Elasticsearch([
    {'host': es_host, 'port': es_port}
])

READ_COUNT_KEY = 'blog:read_count'
ACCESS_COUNT_KEY = 'blog:access_count'
CACHE_KEY = 'blog:post_cache'
UNREAD_COMMENTS_KEY = 'blog:unread_comment_queue'
UNREAD_MESSAGE_KEY = 'blog:unread_message_queue'

IMG_UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'upload')

######## 自定义初始化 ##########
from scripts import *
redis_init()

'''
似乎django有个自动压缩前端所有需要比如css，js这些文件的组件
'''