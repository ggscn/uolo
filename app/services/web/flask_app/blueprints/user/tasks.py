import os
import json

from flask_app.app import make_celery
from flask import url_for
from lib.email_utils import Mailgun
from flask_app.blueprints.user.models import User

from pywebpush import webpush, WebPushException

celery = make_celery()

@celery.task()
def test_task():
    pass

@celery.task()
def send_welcome_email(recipient):
    subject = 'Welcome to Fyllo!'
    template = 'welcome'
    Mailgun().send(recipient, subject, template)

@celery.task()
def send_password_reset_email(recipient, token):
    subject = 'Fyllo password reset'
    template = 'password_reset'

    password_reset_url = '{}?reset_token={}'.format(url_for('user.new_password', _external=True), token)

    email_content_kwargs = {
        'reset_url':password_reset_url
    }

    Mailgun().send(recipient, subject, template, email_content_kwargs)

@celery.task()
def send_password_reset_confirmation_email(recipient):
    subject = 'Fyllo password has been reset'
    template = 'password_reset_success'

    Mailgun().send(recipient, subject, template)