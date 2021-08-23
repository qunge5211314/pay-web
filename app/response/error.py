#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-21
# @Author       : HanQun
# @Introduction : 所有错误响应方法
# dependence
from flask import jsonify
from app.enum import ResponseCode


def server_error():
    from app import db
    db.session.rollback()
    response = jsonify({'code': ResponseCode.SERVER_ERROR.value, 'msg': "服务器异常，请稍后重试"})
    response.status_code = 200
    return response


def custom(code=-1, msg='', data=''):
    from app import db
    db.session.rollback()
    response = jsonify({'code': code, 'msg': msg, 'data': data})
    response.status_code = 200
    return response