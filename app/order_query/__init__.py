#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-27
# @Author       : HanQun
# @Introduction : 订单查询蓝图注册
# dependence
from flask import Blueprint

order_query = Blueprint("order_query", __name__)

from . import query