# -*- coding:utf-8 -*-
import datetime
import logging
import os
import shutil
import traceback
import zipfile

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
                if (today - date).days >= settings.BACKUP_PERIOD:
                    os.remove(os.path.join(backup_dir, 'db.sqlite3.%s' % date.strftime('%Y%m%d')))
            except Exception,e:
                if 'date' in locals():
                    logging.warn('Failed to delete old dbfile [db.sqlite3.%s]' % date.strftime('%Y%m%d'))
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

def upload_backup():
    backup_dir = os.path.join(settings.PROJECT_ROOT, 'backup', 'upload')
    today = datetime.date.today()
    logging.info('Deleting old images...')
    for upload_dir in os.listdir(backup_dir):
        if upload_dir.startswith('upload'):
            try:
                date = datetime.datetime.strptime(os.path.splitext(upload_dir)[1][1:],'%Y%m%d').date()
                if (today - date).days >= settings.BACKUP_PERIOD:
                    os.remove(os.path.join(backup_dir, 'upload.zip.%s' % date.strftime('%Y%m%d')))
            except Exception,e:
                if date in locals():
                    logging.warn('Failed to delete old image dir [upload.zip.%s]' % date.strftime('%Y%m%d'))
                logging.warn('Failed to delete old image dir:\n' + traceback.format_exc(e))
    logging.info('Old image dirs deleted')

    src_dir = os.path.join(settings.BASE_DIR, 'static', 'upload')
    dest_file = os.path.join(settings.PROJECT_ROOT, 'backup', 'upload', 'upload.zip.%s' % today.strftime('%Y%m%d'))
    logging.info('Try to zip up image directory and copy it...')
    try:
        zip_dir(src_dir, dest_file)
    except Exception,e:
        logging.error('Failed to zip up upload dir:\n' + traceback.format_exc(e))
        raise


def zip_dir(dirname,zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else :
        for root, dirs, files in os.walk(dirname):
            for dir in dirs:
                filelist.append(os.path.join(root,dir))
            for name in files:
                filelist.append(os.path.join(root, name))

    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        zf.write(tar,arcname)
    zf.close()