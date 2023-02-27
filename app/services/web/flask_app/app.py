from flask import Flask, request
from celery import Celery
from flask_app.extensions import db, login_manager, bcrypt, csrf, migrate, cors, limiter

from flask_app.blueprints.analysis import analysis
from flask_app.blueprints.user import user
from flask_app.blueprints.user.models import User
from flask_app.blueprints.admin import admin
from flask_app.blueprints.watchlist import watchlist


from werkzeug.middleware.proxy_fix import ProxyFix

login_manager.login_view = "user.login"
login_manager.login_message = u"Logged in!"

CELERY_TASK_LIST = ['flask_app.blueprints.user.tasks','flask_app.blueprints.analysis.tasks']

def create_app(settings_override=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    if settings_override:
        app.config.update(settings_override)

    middleware(app)
    app.register_blueprint(analysis)
    app.register_blueprint(user)
    app.register_blueprint(admin)
    app.register_blueprint(watchlist)
    extensions(app)

    @app.context_processor
    def inject_template_scope():
        injections = dict()

        def cookies_check():
            value = request.cookies.get('cookie_consent')
            return value == 'true'
        injections.update(cookies_check=cookies_check)

        return injections
    return app


def make_celery(app=None):

    app = app or create_app()

    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
        include=CELERY_TASK_LIST
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    limiter.init_app(app)
    return None

def middleware(app):
    app.wsgi_app = ProxyFix(app.wsgi_app)
    return None