#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-26
# @Author       : HanQun
# @Introduction : 支付宝回调接口
# dependence
import json

from app import db
from app.enum import PayState, PayMode
from app.models import PayRecord
from app.response import alipay_response_with_callback
from app.response.error import custom
from app.utils.callback_utils import callback_function
from . import notify_api
from flask import request
from datetime import datetime
from alipay import AliPay


# 支付宝回调接口
@notify_api.route("/alipay", methods=["POST"])
def notify_alipay():
    from app.constant.alipay_constant import APP_ID, NOTIFY_URL, PRIVATE_KEY, PUBLIC_KEY
    data = request.form.to_dict()
    alipay = AliPay(APP_ID, NOTIFY_URL, app_private_key_string=PRIVATE_KEY, alipay_public_key_string=PUBLIC_KEY)
    print(data)
    temp_sign = data.pop("sign")
    check = alipay.verify(data, temp_sign)
    print(check)
    if not check:
        return "FAIL,签名错误"
    out_trade_no = data.get("out_trade_no")
    record = PayRecord.query.filter(PayRecord.out_trade_no==out_trade_no).first()
    # 找不到订单或订单已被支付通知
    if not record:
        return "FAIL,未查询到该订单"
    if record.pay_state != PayState.WAITING.value:
        return "FAIL,已通知的订单"
    if record.pay_mode == PayMode.WECHAT.value:
        setattr(record, "pay_mode", PayMode.ALIPAY.value)
    if data.get("trade_status") in ("TRADE_SUCCESS", "TRADE_FINISHED"):
        setattr(record, "pay_state", PayState.SUCCESS.value)
    else:
        setattr(record, "pay_state", PayState.FAILURE.value)
    setattr(record, "result", data.get("trade_status"))
    setattr(record, "trade_no", data.get("trade_no"))
    setattr(record, "total_fee", int(float(data.get("total_amount", 0.00))*100))
    setattr(record, "receipt_fee", int(float(data.get("receipt_amount", 0.00))*100))
    setattr(record, "pay_time", datetime.strptime(data.get("gmt_payment"), "%Y-%m-%d %H:%M:%S") if data.get("gmt_payment") else None)
    setattr(record, "pay_channel", json.loads(data.get("fund_bill_list", "[{}]"))[0].get("fundChannel"))
    setattr(record, "customer_id", data.get("buyer_id"))
    db.session.add(record)
    return alipay_response_with_callback(callback=callback_function, param=(record,))