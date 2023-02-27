# -*- coding: utf-8 -*-

import os

port = int(os.environ.get('PORT', 5000))
bind = '0.0.0.0:{}'.format(port)
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" in %(D)sµs'
workers=3
worker_class='gevent'
threads=3
worker_connections=1000