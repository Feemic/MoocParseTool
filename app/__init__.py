# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from .plugins.log_class import configure_logger
from .plugins.celery_class import make_celery
import os

redis = Redis()
celery = make_celery(app)
bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
app = Flask(__name__)

def create_app():
    configure_logger()

    config_name = os.getenv('FLASK_CONFIG') or 'default'
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    db.app = app
    db.create_all()

    bootstrap.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    return app