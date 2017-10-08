#-*- coding: utf-8 -*-
import os
from __future__ import absolute_import
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))

class config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret string'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    #new
    
    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'
    CELERY_IMPORTS = ("app.plugins.cron")
    CELERYBEAT_SCHEDULE = {
        'every-30-minutes': {
            'task': 'celery_tasks.server_monitor',
            'schedule': timedelta(minutes=30),
        }
    }
    @staticmethod
    def init_app(app):
        pass

class DafaultConfig(config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/' \
                              'fserver?charset=utf8'

class TestingConfig(config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/' \
                              '' + os.path.join(basedir, 'test')
    CELERY_CONFIG = {'CELERY_ALWAYS_EAGER': True}

config = {
    'testing': TestingConfig,
    'default': DafaultConfig
}
