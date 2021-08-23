#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-23
# @Author       : HanQun
# @Introduction : 微信回调接口
# dependence
from app import db
from app.enum import PayMode, PayState
from app.response import wechat_response_with_callback
from app.utils.callback_utils import callback_function
from . import notify_api
from app.utils.wechat_utils import WeChatNotify
from flask import Response, request
from app.models import PayRecord
from datetime import datetime


@notify_api.route("/wechat", methods=["POST"])
def wechat_pay_notify():
    # 拿到请求xml数据
    xml = request.data.decode("utf-8")
    wechat_notify = WeChatNotify(xml)
    try:
        data = wechat_notify.special_xml_to_dict(xml)
    except Exception as e:
        print(e)
        return Response(wechat_notify.return_data("FAIL", "xml解析错误"), mimetype="application/xml")
    check_result = wechat_notify.check_sign(**data)
    if not check_result:
        return Response(wechat_notify.return_data("FAIL", "签名错误"), mimetype="application/xml")
    out_trade_no = data.get("out_trade_no", None)
    record = PayRecord.query.filter(PayRecord.out_trade_no == out_trade_no).first()
    # 找不到订单或订单已被支付通知
    if not record or record.pay_state != PayState.WAITING.value:
        return Response(wechat_notify.return_data("FAIL", "out_trade_no不存在"), mimetype="application/xml")
    if record.pay_state != PayState.WAITING.value:
        return Response(wechat_notify.return_data("FAIL", "已通知订单记录"), mimetype="application/xml")
    # 已更换使用阿里支付的订单
    if record.pay_mode == PayMode.ALIPAY.value:
        setattr(record, "pay_mode", PayMode.WECHAT.value)
    # 回调处理
    if data.get("result_code") == "SUCCESS":
        setattr(record, "pay_state", PayState.SUCCESS.value)
    else:
        setattr(record, "pay_state", PayState.FAILURE.value)
    setattr(record, "result", data.get("result_code"))
    setattr(record, "trade_no", data.get("transaction_id"))
    setattr(record, "total_fee", data.get("total_fee"))
    setattr(record, "receipt_fee", data.get("cash_fee"))
    setattr(record, "pay_time", datetime.strptime(data.get("time_end"), "%Y%m%d%H%M%S") if data.get("time_end") else None)
    setattr(record, "pay_channel", data.get("bank_type"))
    setattr(record, "customer_id", data.get("openid"))
    db.session.add(record)
    return wechat_response_with_callback("SUCCESS", "OK", callback=callback_function, param=(record,))
