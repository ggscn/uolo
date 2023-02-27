import enum
from flask import current_app
from collections import OrderedDict

from sqlalchemy import DateTime, Date, Column, Integer, String, Boolean, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from typing import List

from lib.sqlalchemy_utils import ModelUtils, EnumUtils

from flask_login import UserMixin
from flask_app.extensions import db, bcrypt

from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer


class RoleEnum(EnumUtils, enum.Enum):
    ADMIN = 'ADMIN'
    FREE_MEMBER = 'FREE_MEMBER'
    PAID_MEMBER_TIER_1 = 'PAID_MEMBER_1'
    PAID_MEMBER_TIER_2 = 'PAID_MEMBER_2'
    PAID_MEMBER_TIER_3 = 'PAID_MEMBER_3'



class User(db.Model, ModelUtils, UserMixin):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    
    email = Column(String(255), unique=True, nullable=False)
    slug = Column(String(255))
    password_hash = Column(String(255), nullable=False, server_default='')
    role = Column(Enum(RoleEnum), nullable=False, server_default='FREE_MEMBER')
    is_enabled = Column('is_enabled', Boolean(), nullable=False,server_default='1')
    accept_tos = Column(Boolean(), nullable=False,server_default='0')
    
    watchlists: Mapped[List["Watchlist"]] = relationship(cascade="all, delete",)


    def __repr__(self):
        return '<User %r>' % self.email

    def __init__(self, **kwargs):

        super(User, self).__init__(**kwargs)

    @classmethod
    def with_email(cls, email):
        return User.query.filter(User.email == email).first()
    @classmethod
    def hash_password(cls, plaintext_password):
        password_hash = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')
        return password_hash

    def is_authenticated(self, plaintext_password):
        return bcrypt.check_password_hash(self.password_hash, plaintext_password)

    @classmethod
    def decrypt_token(cls, token):
        secret_key = current_app.config['SECRET_KEY']
        serializer = Serializer(secret_key)
        try:
            plaintext_token = serializer.loads(token)
            return plaintext_token
        except Exception as e:
            print(e)
            return None

    @classmethod
    def find_by_slug(cls, slug):
        return User.query.filter(User.slug == slug).first()


    def delete(self):
        db.session.delete(self)
        db.session.commit()