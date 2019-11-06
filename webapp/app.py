from flask import Flask
# from flask_login import current_user
from importlib import import_module

from config.settings import config
from utils.functions import mail
from .extensions import csrf  #, db, login_manager

# Azure configuration > general settings > Startup Command:
# gunicorn --bind=0.0.0.0 --timeout 1200 webapp.app:create_app()
# gunicorn --bind=0.0.0.0 --timeout 600 hello:app

# Local Docker
# gunicorn -w 2 -b :19000 --reload "webapp.app:create_app()"


def create_app():
    app = Flask(__name__)
    config_app(app)
    register_blueprints(app)
    init_extensions(app)
    return app


def register_blueprints(app):
    for module_name in ('blueprints.base',):
        module = import_module(f'webapp.{module_name}.views')
        app.register_blueprint(module.blueprint)


def config_app(app):
    # app.config settings
    app.config.from_object(config)
    app.config['DEV'] = False

    # Flask-Mail settings via Azure ENV and below
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    # Sanity check config settings
    assert app.config['MAIL_DEFAULT_SENDER'] == 'frank@aixpact.com', 'Flask-Mail settings failed'
    assert config.FRANK == 'test this environmental value', 'config settings failed'
    assert config.FRANK == app.config['FRANK'], 'config settings failed'
    assert app.config['SECRET_KEY'] == config.SECRET_KEY, 'SECRET_KEY not set'


def init_extensions(app):
    #
    csrf.init_app(app)
    mail.init_app(app)
    # db.init_app(app)
    # login_manager.init_app(app)

#
app = create_app()
