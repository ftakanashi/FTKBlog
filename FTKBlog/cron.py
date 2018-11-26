# -*- coding:utf-8 -*-
import datetime
import hashlib
import logging
import os
import shutil
import traceback
import zipfile

from django.conf import settings

logger = logging.getLogger('django.ftkblog.cron')

def get_hash(file):
    md5 = hashlib.md5()
    with open(file, 'rb') as f:
        md5.update(f.read())
    return md5.hexdigest()

def check_newest(backup_dir, dest_file):
    logger.info('Checking newest files. Deleting identical backup...')
    for file in sorted(os.listdir(backup_dir), key=lambda x: os.stat(os.path.join(backup_dir, x)).st_mtime, reverse=True)[:5]:
        full_path = os.path.join(backup_dir, file)
        if full_path == dest_file: continue
        if get_hash(full_path) == get_hash(dest_file):
            logger.info('Locating [%s] the identical backup as [%s]' % (full_path, dest_file))
            try:
                logger.info('Deleting identical file [%s]' % full_path)
                os.remove(full_path)
            except Exception,e:
                logger.error('Failed to remove identical file [%s]' % full_path)
    logger.info('Newest files checked.')


def db_backup():
    backup_dir = os.path.join(settings.PROJECT_ROOT,'backup','db')
    today = datetime.date.today()
    logger.info('Deleting old dbfiles...')
    src = os.path.join(settings.PROJECT_ROOT,'db','db.sqlite3')
    for dbfile in os.listdir(backup_dir):
        if dbfile.startswith('db.sqlite3'):
            try:
                date = datetime.datetime.strptime(os.path.splitext(dbfile)[1][1:],'%Y%m%d').date()
            except Exception,e:
                logger.warn('Failed to specify the date for [%s]' % dbfile)
            try:
                if (today - date).days >= settings.BACKUP_PERIOD:
                    os.remove(os.path.join(backup_dir, 'db.sqlite3.%s' % date.strftime('%Y%m%d')))
            except Exception,e:
                if 'date' in locals():
                    logger.warn('Failed to delete old dbfile [db.sqlite3.%s]' % date.strftime('%Y%m%d'))
                logger.warn('Failed to delete old dbfile:\n' + traceback.format_exc(e))

    logger.info('Deleted old dbfiles')

    logger.info('Try to copy dbfile.')
    try:
        shutil.copy(src, backup_dir)
    except Exception,e:
        logger.error('Failed to copy db.sqlite3:\n' + traceback.format_exc(e))
        raise
    DATE = datetime.date.today().strftime('%Y%m%d')
    logger.info('renaming dbfile...')
    try:
        os.rename(os.path.join(backup_dir,'db.sqlite3'),os.path.join(backup_dir,'db.sqlite3.%s' % DATE))
    except Exception,e:
        logger.error('Failed to rename dbfile\n' + traceback.format_exc(e))
        raise

    logger.info('Backup over to: ' + os.path.join(settings.PROJECT_ROOT, 'backup', 'db', 'db.sqlite3.%s' % DATE))

def upload_backup():
    backup_dir = os.path.join(settings.PROJECT_ROOT, 'backup', 'upload')
    today = datetime.date.today()
    logger.info('Deleting old images...')
    for upload_dir in os.listdir(backup_dir):
        if upload_dir.startswith('upload'):
            try:
                date = datetime.datetime.strptime(os.path.splitext(upload_dir)[1][1:],'%Y%m%d').date()
                if (today - date).days >= settings.BACKUP_PERIOD:
                    os.remove(os.path.join(backup_dir, 'upload.zip.%s' % date.strftime('%Y%m%d')))
            except Exception,e:
                if 'date' in locals():
                    logger.warn('Failed to delete old image dir [upload.zip.%s]' % date.strftime('%Y%m%d'))
                logger.warn('Failed to delete old image dir:\n' + traceback.format_exc(e))
    logger.info('Old image files deleted')

    src_dir = os.path.join(settings.BASE_DIR, 'static', 'upload')
    dest_file = os.path.join(backup_dir, 'upload.zip.%s' % today.strftime('%Y%m%d'))
    logger.info('Try to zip up image directory and copy it...')
    try:
        zip_dir(src_dir, dest_file)
    except Exception,e:
        logger.error('Failed to zip up upload dir:\n' + traceback.format_exc(e))
        raise

    check_newest(backup_dir, dest_file)


def migration_backup():

    backup_dir = os.path.join(settings.PROJECT_ROOT, 'backup', 'migration')
    logger.info('Deleting old migrations...')
    today = datetime.date.today()
    for migration in os.listdir(backup_dir):
        if migration.startswith('migration'):
            try:
                date = datetime.datetime.strptime(os.path.splitext(migration)[1][1:],'%Y%m%d')
                if (today - date).days >= settings.BACKUP_PERIOD:
                    os.remove(os.path.join(backup_dir, migration))
            except Exception,e:
                if 'date' in locals():
                    logger.warn('Failed to delete old migration [migration.zip.%s]' % date.strftime('%Y%m%d'))
                else:
                    logger.warn('Failed to delete old migration:\n' + traceback.format_exc(e))

    logger.info('Old migrations are deleted')

    target_dirs = []
    dest_dir = os.path.join(settings.PROJECT_ROOT, 'backup', 'migration')
    for root,dirs,files in os.walk(settings.BASE_DIR):
        if 'migrations' in dirs:
            target_dirs.append(os.path.join(root,'migrations'))

    for dir in target_dirs:
        app = os.path.basename(os.path.dirname(dir))
        backup_dir = os.path.join(dest_dir, app)
        if not os.path.isdir(backup_dir):
            os.makedirs(backup_dir)
        logger.info('Zipping up migrations in [%s]' % app)
        dest_file = os.path.join(backup_dir, '%s.migrations.zip.%s' % (app, today.strftime('%Y%m%d')))
        try:
            zip_dir(dir, dest_file)
        except Exception,e:
            logger.error('Failed to zip up migration dir:\n[%s]\n%s' % (dir, traceback.format_exc(e)))
            raise
        check_newest(backup_dir, dest_file)

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