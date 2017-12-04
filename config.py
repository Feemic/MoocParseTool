# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret string'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    JOBS_DIR = 'app.plugins.scheduler_jobs:'
    JOBS = [
        {
            'id': 'blog_update_all',
            'func': '%scheck_blog_update' % JOBS_DIR,
            'args': None,
            'trigger': 'interval',
            'hours': 24*2
        },

    ]

    @staticmethod
    def init_app(app):
        pass


class DafaultConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:password@localhost/data?charset=utf8'


config = {
    'default': DafaultConfig
}
