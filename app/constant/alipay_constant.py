#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-21
# @Author       : HanQun
# @Introduction : 支付宝支付相关参数
# dependence
from flask import current_app
from manager import app

APP_ID = "2019011463005038"
QRCODE_PREFIX = "https://openapi.alipay.com/gateway.do?"

with app.app_context():
    NOTIFY_URL = current_app.config["SERVER_URL"] + "/daka_pay/notify/alipay"
    PRIVATE_KEY = open(current_app.root_path + '/alipay_keys/rsa_private_key.pem').read()
    PUBLIC_KEY = open(current_app.root_path + '/alipay_keys/rsa_public_key.pem').read()