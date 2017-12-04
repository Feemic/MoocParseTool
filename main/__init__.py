from flask import Blueprint
main = Blueprint('main', __name__, static_url_path='', static_folder='')

from . import views, view_errors, view_mooc
