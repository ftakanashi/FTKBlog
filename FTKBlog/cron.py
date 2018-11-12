# -*- coding:utf-8 -*-
import datetime
import logging
import os
import shutil
import traceback

from django.conf import settings

DATEFMT = '%Y-%m-%d %H:%M:%S'
CRONLOG = os.path.join(settings.PROJECT_ROOT, 'logs', 'cron', 'cron.log')

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(filename)s [L.%(lineno)d] %(levelname)s  %(message)s',
                    datefmt=DATEFMT, filename=CRONLOG)

def db_backup():
    backup_dir = os.path.join(settings.PROJECT_ROOT,'backup','db')
    today = datetime.date.today()
    logging.info('Deleting old dbfiles...')
    for dbfile in os.listdir(backup_dir):
        if dbfile.startswith('db.sqlite3'):
            try:
                date = datetime.datetime.strptime(os.path.splitext(dbfile)[1][1:],'%Y%m%d').date()
                if (today - date).days >= 30:
                    os.remove(os.path.join(backup_dir, 'db.sqlite3.%s' % date.strftime('%Y%m%d')))
            except Exception,e:
                logging.warn('Failed to delete old dbfile:\n' + traceback.format_exc(e))

    logging.info('Deleted old dbfiles')

    src = os.path.join(settings.PROJECT_ROOT,'db','db.sqlite3')
    logging.info('Try to copy dbfile.')
    try:
        shutil.copy(src, backup_dir)
    except Exception,e:
        logging.error('Failed to copy db.sqlite3:\n' + traceback.format_exc(e))
        raise
    DATE = datetime.date.today().strftime('%Y%m%d')
    logging.info('renaming dbfile...')
    try:
        os.rename(os.path.join(backup_dir,'db.sqlite3'),os.path.join(backup_dir,'db.sqlite3.%s' % DATE))
    except Exception,e:
        logging.error('Failed to rename dbfile\n' + traceback.format_exc(e))
        raise

    logging.info('Backup over to: ' + os.path.join(settings.PROJECT_ROOT, 'backup', 'db', 'db.sqlite3.%s' % DATE))
