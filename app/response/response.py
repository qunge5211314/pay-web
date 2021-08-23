#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-21
# @Author       : HanQun
# @Introduction : 所有正常响应方法
# dependence
from flask import jsonify
from app.enum import ResponseCode
from .error import server_error

def succeed(message='', data=''):
    print(data)
    response = jsonify({'code': ResponseCode.SUCCESS.value, 'msg': message, 'data': data})
    response.status_code = 200
    return response


def usually(message='', data=''):
    from app import db
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return server_error()
    return succeed(message, data)


def alipay_response_with_callback(callback=None, param=()):
    from app import db
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return server_error()

    if callback:
        callback(*param)
        return "success"
    else:
        return "success"


def wechat_response_with_callback(state, msg, callback=None, param=()):
    from app import db
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return "<xml><return_code><![CDATA[{state}]]></return_code><return_msg><![CDATA[{msg}]></return_msg></xml>".format(
            state="FAIL", msg="服务器异常")
    if callback:
        callback(*param)
    return "<xml><return_code><![CDATA[{state}]]></return_code><return_msg><![CDATA[{msg}]></return_msg></xml>".format(
            state=state, msg=msg)


