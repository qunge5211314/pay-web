#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-21
# @Author       : HanQun
# @Introduction : app初始化
# dependence
from flask import Flask
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_cors import CORS
from request_healthy import Healthy

db = SQLAlchemy()
redis_store = FlaskRedis()
request_healty = Healthy()


def create_app(config_name):
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object(config[config_name])
    db.app = app
    db.init_app(app)
    redis_store.init_app(app)
    request_healty.init_app(app)
    from .prepay_api import prepay_api as prepay_api_blueprint
    app.register_blueprint(prepay_api_blueprint, url_prefix='/daka_pay/prepay')
    from .notify_api import notify_api as notify_api_blueprint
    app.register_blueprint(notify_api_blueprint, url_prefix='/daka_pay/notify')
    from .order_query import order_query as order_query_blueprint
    app.register_blueprint(order_query_blueprint, url_prefix='/daka_pay/order_query')
    return app
