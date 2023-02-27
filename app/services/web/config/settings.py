import os
from celery.schedules import crontab

LOG_LEVEL = 'INFO'

DEBUG = True

SERVER_NAME = os.environ.get('SITE_URL','65.21.245.213:5000')
SECRET_KEY = os.environ.get('SECRET_KEY')
SERVICE_ACCOUNT_PATH = os.environ.get('SERVICE_ACCOUNT_PATH')

MAX_CONTENT_LENGTH = 16 * 1024 * 1024

db_uri = os.environ.get('DATABASE_URL')
SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_TRACK_MODIFICATIONS = False

CELERY_BROKER_URL = os.environ.get('REDIS_URL')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
accept_content = ['json']
task_serializer = 'json'
result_serializer = 'json'
redis_max_connections = 10
CELERYBEAT_SCHEDULE = {}