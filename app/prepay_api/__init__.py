#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-21
# @Author       : HanQun
# @Introduction : api注册
# dependence
from flask import Blueprint

prepay_api = Blueprint("prepay_api", __name__)
from . import alipay_prepay, wechat_prepay