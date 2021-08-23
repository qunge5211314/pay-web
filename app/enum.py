#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-21
# @Author       : HanQun
# @Introduction : 支付服务相关枚举值
# dependence
from enum import IntEnum


# 全局响应码
class ResponseCode(IntEnum):
    SUCCESS = 200,
    REPEAT_ORDER = -100
    PARAM_ERROR = -101
    INTERNET_ENV = -102
    SERVER_ERROR = -103
    NOT_SUPPORT = -104
    NOT_FOUND = -105



# 支付状态
class PayState(IntEnum):
    WAITING = 0,
    SUCCESS = 1,
    FAILURE = 2,
    REFUNDING = 3,
    REFUNDED = 4


# 支付方式
class PayMode(IntEnum):
    WECHAT = 0,
    ALIPAY = 1,
    APPLE = 2


# 支付类型
class PayType(IntEnum):
    APP = 0,
    APPLET = 1,
    QRCODE = 2,
    WAP = 3,
    JSAPI = 4



class CheckType(IntEnum):
    INT = 0,
    EMAIL = 1,
    PHONE = 2,
    NOEMOJI = 3,
    JSON = 4,
    DATE = 5,
    DATETIME = 6,
    TIMEHM = 7,
    FLOAT = 8,
    DATETIMEHM = 9,
    PASSWORD = 10,
    TELEPHONE = 11,
    TIME = 12,
    OTHER = 999


class WechatTradeType(IntEnum):
    APP = 0,
    JSAPI = 1,
    NATIVE = 2


class NotifyState(IntEnum):
    WAITING = 0,  # 待通知
    Notified = 1  # 已通知