import os
import json
from datetime import date

from flask_app.blueprints.user.models import User
from flask_app.blueprints.plant.models import Plant

from pywebpush import webpush, WebPushException


def send_push_notification(user_id, message):
    u = User.query.get(user_id)

    data = {
        'message':message,
        'title':'Fyllo Update'
    }

    try:
        webpush(
            subscription_info={
                "endpoint": u.webpush_endpoint,
                "keys": {
                    "p256dh": u.webpush_p256dh,
                    "auth": u.webpush_auth
            }},
            data=json.dumps(data),
            vapid_private_key=os.environ.get('WEBPUSH_PRIVATE_KEY'),
            vapid_claims={
                "sub": "mailto:YourNameHere@example.org"
            }
        )
    except WebPushException as ex:
        print("I'm sorry, Dave, but I can't do that: {}", repr(ex))
        # Mozilla returns additional information in the body of the response.
        if ex.response and ex.response.json():
            extra = ex.response.json()
            print("Remote service replied with a {}:{}, {}",
                extra.code,
                extra.errno,
                extra.message
            )