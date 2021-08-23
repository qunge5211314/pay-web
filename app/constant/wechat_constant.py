#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-21
# @Author       : HanQun
# @Introduction : 微信支付相关参数
# dependence
from flask import current_app
from manager import app

APP_SECRET = ""
API_KEY = ""
with app.app_context():
    NOTIFY_URL = current_app.config["SERVER_URL"] + "/daka_pay/notify/wechat"
PREPAY_URL = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
APP_ID = ""
APPLET_ID = ""
APP_MCH_ID = ""
APPLET_MCH_ID = ""
H5_APP_ID = ""
H5_MCH_ID = ""
JSAPI_APP_ID = ""
JSAPI_MCH_ID = ""
