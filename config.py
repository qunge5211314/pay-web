#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-
# @Author       : HanQun
# @Introduction : 打卡助手支付服务相关配置文件
# dependence
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # 秘钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pay.com'
    # 配置
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 50


# 开发测试环境配置
class DevelopConfig(Config):
    DEBUG = True
    SERVER_URL = "http://localhost" # 本服务的公网地址端口，用于微信、支付宝回调使用
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/pay?charset=utf8mb4' # mysql配置
    SENTRY_DSN = 'http://f1e82cdb492747fe8a93d434f4da498c:13a83349c62742babce3d5e8d239230d@47.93.42.146:9000/34' # sentry配置
    REDIS_URL = "redis://:pay@localhost:6379/0" # redis配置
    APPSTORE_CHECKURL = 'https://sandbox.itunes.apple.com/verifyReceipt' # 苹果支付配置
    MICRO_SERVICE_AUTHORIZATION_GATE_WAY_ADMIN = "http://172.27.106.18:8001" # 微服务网关管理器地址配置


# 生产环境配置
class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopConfig,
    'production': ProductionConfig,
    'default': DevelopConfig
}
