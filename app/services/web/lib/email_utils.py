import os
import requests

from flask import current_app

class Mailgun(object):
    def __init__(self):
        self.public_key = os.environ.get('MAILGUN_PUBLIC')
        self.private_key = os.environ.get('MAILGUN_PRIVATE')
        self.domain_name = 'sandboxa6979dc6cc244e4b89ff305970a16511.mailgun.org'
        self.sender = 'sender'
        self.base_url = 'https://api:{}@api.mailgun.net/v3/{}{}'

    def request(self, method, endpoint, params=None):
        url = self.base_url.format(
            self.private_key, 
            self.domain_name, 
            endpoint
        )
        print(url)
        response = requests.request(method, url, data=params)

        if response.status_code != 200:
            raise Exception('Email not send')
        return response

    def send(self, recipient, subject, template, email_content_kwargs=None):
        sender = self.sender
        method = 'POST'
        endpoint = '/messages'

        html_path = os.path.join('flask_app/templates/email', '{}.html'.format(template))

        with open(html_path, 'r') as f:
            html = f.read()
            if email_content_kwargs is not None:
                html = format_email(html, email_content_kwargs)

        params = {
            'from': sender,
            'to': recipient,
            'subject': subject,
            'html': html
        }

        self.request(method, endpoint, params)

def format_email(email_content, email_content_kwargs):
    result = email_content.replace("{", "{{").replace("}", "}}").replace("^[[", "{").replace("]]^", "}").format(**email_content_kwargs)
    return result