#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-22
# @Author       : HanQun
# @Introduction : 预支付相关装饰器
# dependence
import re
import json
import functools

from app.enum import CheckType, PayState, ResponseCode, PayType, PayMode
from app.models import PayRecord
from ..response.error import custom
from ..utils.ip_utils import is_internal_ip
from datetime import datetime
from flask import has_request_context, _request_ctx_stack, request
from werkzeug.local import LocalProxy

current_record = LocalProxy(lambda: get_record())


def get_record():
    if has_request_context() and not hasattr(_request_ctx_stack.top, 'record'):
        return None
    return getattr(_request_ctx_stack.top, 'record', None)


# 内网环境要求装饰器
def internal_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if is_internal_ip(request.remote_addr):
            return func(*args, **kwargs)
        else:
            return custom(code=ResponseCode.INTERNET_ENV.value, msg='仅供内网环境调用')

    return wrapper


def request_params_value_check(name, required, value, check):
    from app.enum import CheckType
    res = value
    if required:
        if not value and not isinstance(value, int):
            return "%s不能为空" % name, res

    if check == CheckType.INT:
        if value:
            try:
                res = int(value)
            except Exception as e:
                return "%s应为整数" % name, res

    elif check == CheckType.EMAIL:
        if value and not re.compile(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$').match(value):
            return "%s应为email格式" % name, res

    elif check == CheckType.PHONE:
        if value and not re.compile(r"^1\d{10}$").match(value):
            return "%s应为电话号码" % name, res

    elif check == CheckType.NOEMOJI:
        if value and not re.compile(r'^[a-zA-Z0-9\u4E00-\u9FA5]+$').match(value):
            return "%s包含非法字符" % name, res

    elif check == CheckType.JSON:
        if value:
            try:
                res = json.loads(value)
            except Exception as e:
                return "%s应为JSON格式" % name, res

    elif check == CheckType.DATETIME:
        if value:
            try:
                res = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except Exception as e:
                return "%s应为datetime:格式" % name, res

    elif check == CheckType.DATE:
        if value:
            try:
                res = datetime.strptime(value, '%Y-%m-%d').date()
            except Exception as e:
                return "%s应为date格式" % name, res
    elif check == CheckType.TIME:
        if value:
            try:
                res = datetime.strptime(value, '%H:%M:%S').time()
            except Exception as e:
                return '%s应为HH:MM:SS格式' % name, res
    elif check == CheckType.TIMEHM:
        if value:
            try:
                if len(value) == 5:
                    res = datetime.strptime(value, '%H:%M').time()
                else:
                    res = datetime.strptime(value, "%H:%M:%S").time()
            except Exception as e:
                return '%s应为HH:MM格式' % name, res
    elif check == CheckType.FLOAT:
        if value:
            try:
                res = float(value)
            except Exception as e:
                return '%s应为Float格式' % name, res
    elif check == CheckType.DATETIMEHM:
        if value:
            try:
                res = datetime.strptime(value, '%Y-%m-%d %H:%M')
            except Exception as e:
                return '%s应为Y-M-D H:M格式' % name, res
    elif check == CheckType.TELEPHONE:
        if value and not re.compile(r"^1\d{10}$").match(value):
            return "%s应该是手机号码格式" % name, res

    return None, res


# 校验请求参数
def check_request_params(**checks):
    def check_request_params_func(func=None):
        @functools.wraps(func)
        def test(*args, **kwargs):
            errors = []
            for key, parm in checks.items():
                name = parm[0]
                if request.method == 'POST':
                    value = request.form.get(key)
                else:
                    value = request.args.get(key)
                required = parm[1]
                check = parm[2]
                error, res = request_params_value_check(name, required, value, check)
                kwargs[key] = res
                if error:
                    errors.append(error)

            if errors:
                return custom(code=ResponseCode.PARAM_ERROR.value, msg=','.join(errors))
            return func(*args, **kwargs)

        return test

    return check_request_params_func


# 校验订单
def order_check(func):
    @functools.wraps(func)
    @check_request_params(out_trade_no=("订单编号", True, CheckType.OTHER),
                          pay_type=("支付类型", True, CheckType.INT),
                          customer_id=("用户id", False, CheckType.OTHER),
                          invalid_time=("订单失效时间", False, CheckType.DATETIME))
    def wrapper(*args, **kwargs):
        record = PayRecord.query.filter(PayRecord.out_trade_no == kwargs.get("out_trade_no")).first()
        if record and record.pay_state == PayState.SUCCESS.value:
            return custom(ResponseCode.REPEAT_ORDER.value, "已支付订单,请勿重复支付")
        if kwargs.get("pay_type") == PayType.QRCODE.value and kwargs.get("customer_id"):
            return custom(ResponseCode.PARAM_ERROR.value, "二维码支付不可传递用户id")
        if kwargs.get("pay_type") == PayType.APP.value and kwargs.get("customer_id"):
            return custom(ResponseCode.PARAM_ERROR.value, "APP支付不可传递用户id")
        if kwargs.get("invalid_time") and kwargs.get("invalid_time") <= datetime.now():
            return custom(ResponseCode.PARAM_ERROR.value, "失效时间不能小于当前时间")
        _request_ctx_stack.top.record = record
        return func(*args, **kwargs)

    return wrapper
