from sqlalchemy import DateTime

from lib.datetime_utils import now_utc

from flask_app.extensions import db

import uuid
from urllib.parse import quote_plus

class EnumUtils:
    def __str__(self):
        return str(self.name).capitalize().replace('_',' ')

    @classmethod
    def choices(cls):
        return [(member.value, name.replace('_',' ').capitalize()) for name, member in cls.__members__.items()]

class ModelUtils(object):

    datetypes = ['datetime.datetime','datetime.date','datetime','date']

    date_created = db.Column(
        DateTime(timezone=True),default=now_utc)
    date_updated = db.Column(
        DateTime(timezone=True),default=now_utc,onupdate=now_utc)

    def save(self):
        db.session.add(self)
        db.session.commit()

        return self

    @classmethod
    def sort_by(cls, field, direction):

        if field not in cls.__table__.columns:
            field = 'created_on'

        if direction not in ('asc', 'desc'):
            direction = 'asc'

        return field, direction

    @classmethod
    def serialize_query(cls, query, is_paginated=False, stringify_dates=True):
        query_results = {}
        query_results['items'] = [] 

        if is_paginated:
            rows = query.items
            query_results['page'] = query.page
            query_results['has_next'] = query.has_next
            query_results['next_num'] = query.next_num
            query_results['has_prev'] = query.has_prev
            query_results['prev_num'] = query.prev_num
            query_results['pages'] = [str(x) for x in query.iter_pages(
                left_edge=1, left_current=2, right_current=3, right_edge=1)]
        else:
            rows = query

        for row in rows:
            item = {}
            for k, v in row.__dict__.items():
                if str(k).startswith("_"):
                    continue
                if stringify_dates and type(v).__name__ in cls.datetypes:
                    item[k] = v.strftime('%Y-%m-%d')
                else:
                    item[k] = str(v)
            query_results['items'].append(item)
                
        return query_results

    @classmethod
    def find_by_slug(cls, slug):
        return cls.query.filter(cls.slug == slug).first()
    
    @classmethod
    def generate_slug(cls, name, uuid_char_len=8):
        return '{}-{}'.format(
            quote_plus(name.replace(' ','-').replace('@','-').replace('.','').lower()), 
            uuid.uuid4().hex[:uuid_char_len]
        )

def init_db():
    db.drop_all()
    db.create_all()