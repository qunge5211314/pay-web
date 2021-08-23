#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-21
# @Author       : HanQun
# @Introduction : 支付宝支付相关接口
# dependence
from datetime import datetime
from decimal import Decimal
from app import db
from app.enum import PayMode, ResponseCode, CheckType, PayType
from app.response import usually
from app.response.error import custom
from app.utils.record_utils import create_record
from . import prepay_api
from ..decorators.prepay_decorator import internal_required, order_check, current_record, check_request_params
from alipay import AliPay


# 支付宝预支付接口
@prepay_api.route("/alipay", methods=["POST"])
@order_check
# @internal_required
@check_request_params(rmb=("订单金额", True, CheckType.INT),
                      title=("订单标题", True, CheckType.OTHER),
                      detail=("订单详情", False, CheckType.OTHER),
                      notify_url=("回调接口url", True, CheckType.OTHER),
                      spbill_create_ip=("客户端ip", False, CheckType.OTHER),
                      return_url=("return_url", False, CheckType.OTHER))
def alipay_prepay(**kwargs):
    from app.constant.alipay_constant import APP_ID, NOTIFY_URL, PRIVATE_KEY, PUBLIC_KEY, QRCODE_PREFIX
    if current_record and current_record.pay_mode == PayMode.ALIPAY.value \
            and current_record.pay_type == PayType.QRCODE.value and current_record.pay_type != kwargs.get("pay_type"):
        return custom(ResponseCode.REPEAT_ORDER.value, "同一订单不可出现多种充值类型")
    elif current_record and current_record.pay_mode == PayMode.ALIPAY.value \
            and current_record.pay_type in [PayType.APP.value, PayType.WAP.value] and kwargs.get(
        "pay_type") == PayType.QRCODE.value:
        return custom(ResponseCode.REPEAT_ORDER.value, "同一订单不可出现多种充值类型")
    kwargs.update({"pay_mode": PayMode.ALIPAY.value})
    record = create_record(current_record, **kwargs)
    if kwargs.get("invalid_time"):
        timeout_express = "%.0fm" % (Decimal((kwargs.get("invalid_time") - datetime.now()).seconds) / Decimal(60))
    else:
        timeout_express = ""
    alipay = AliPay(APP_ID, NOTIFY_URL, app_private_key_string=PRIVATE_KEY, alipay_public_key_string=PUBLIC_KEY)
    if record.pay_type == PayType.APP.value:
        order_string = alipay.api_alipay_trade_app_pay(record.title,
                                                       record.out_trade_no,
                                                       float(round(Decimal(record.rmb) / Decimal(100), 2)),
                                                       timeout_express=timeout_express,
                                                       body=record.detail if record.detail else "")
    elif record.pay_type == PayType.WAP.value:
        order_string = alipay.api_alipay_trade_wap_pay(record.title,
                                                       record.out_trade_no,
                                                       float(round(Decimal(record.rmb) / Decimal(100), 2)),
                                                       timeout_express=timeout_express,
                                                       body=record.detail if record.detail else "",
                                                       buyer_id=record.customer_id,
                                                       return_url=kwargs.get("return_url") if kwargs.get("return_url") else None)
    elif record.pay_type == PayType.QRCODE.value:
        order_string = alipay.api_alipay_trade_page_pay(record.title,
                                                        record.out_trade_no,
                                                        float(round(Decimal(record.rmb) / Decimal(100), 2)),
                                                        timeout_express=timeout_express,
                                                        body=record.detail,
                                                        return_url=kwargs.get("return_url") if kwargs.get("return_url") else None)
    else:
        return custom(ResponseCode.PARAM_ERROR.value, "暂不支持其它交易类型")
    setattr(record, "prepay_info", order_string)
    setattr(record, "qrcode_url", (QRCODE_PREFIX + order_string) if record.pay_type != PayType.APP.value else None)
    db.session.add(record)
    return usually("", {"aliSignedOrder": order_string,
                        "qrcode_url": (QRCODE_PREFIX + order_string) if record.pay_type != PayType.APP.value else ""})
