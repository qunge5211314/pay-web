#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-21
# @Author       : HanQun
# @Introduction : model相关基类和mixin类
# dependence
import time

from app import db
from sqlalchemy.ext.declarative import AbstractConcreteBase, declared_attr
from sqlalchemy import DateTime, Date, Time
from datetime import datetime
from sqlalchemy import func


class JSONBaseMixin(object):
    def to_json(self, exclude_list=()):
        d = {}
        for col in self.__table__.columns:

            col_name = col.name

            if col_name in exclude_list:
                continue

            value = getattr(self, col_name)
            if value is None:
                value = ""
            else:
                if isinstance(col.type, DateTime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(col.type, Date):
                    value = value.strftime('%Y-%m-%d')
                elif isinstance(col.type, Time):
                    value = value.strftime('%H:%M:%S')
            d[col_name] = value
        return d


class BaseModel(AbstractConcreteBase, db.Model, JSONBaseMixin):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, comment='主键')
    create_time = db.Column(db.DateTime, server_default=func.now(), default=datetime.now, index=True, comment='记录创建时间')
    timestamp = db.Column(db.Integer, default=time.time, index=True, comment='记录创建时间戳')
    is_valid = db.Column(db.Boolean, default=True, index=True, comment='是否可用记录')
    update_time = db.Column(db.DateTime, server_default=func.now(), default=datetime.now, onupdate=datetime.now,
                            index=True, comment='记录更新时间')

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
