from __future__ import annotations
import enum

from flask import current_app
from collections import OrderedDict
from datetime import datetime, timedelta

from sqlalchemy import DateTime, Date, Column, Integer, String, Boolean, Enum, Float, ForeignKey, and_, Numeric, desc
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from typing import List

from flask_app.blueprints.user.models import User
from lib.sqlalchemy_utils import ModelUtils, EnumUtils
from flask_app.extensions import db



class Watchlist(db.Model, ModelUtils):
    __tablename__ = 'watchlists'
    id = Column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    items: Mapped[List["WatchlistItem"]] = relationship()

class WatchlistItem(db.Model, ModelUtils):
    __tablename__ = 'watchlist_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(30))
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlists.id", ondelete="CASCADE"))

    
    def __init__(self, **kwargs):
        super(WatchlistItem, self).__init__(**kwargs)