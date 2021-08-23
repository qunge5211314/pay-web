#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-23
# @Author       : HanQun
# @Introduction : 第三方回调通知后回调函数在这定义
# dependence
import requests
import json
from app.enum import NotifyState
from app.constant import AUTH


def callback_function(record):
    from app import db
    headers = {"Content-Type": "application/json", "Authorization": AUTH}
    print(headers)
    params = {"outTradeNo": record.out_trade_no,
              "payState": record.pay_state,
              "payMode": record.pay_mode,
              "payType": record.pay_type}
    res = requests.post(
        record.notify_url,
        json=params,
        headers=headers,
        timeout=5)
    try:
        res.raise_for_status()
    except Exception as e:
        print(e)
        return
    data = json.loads(res.content.decode("utf-8"))
    if data.get("code") != 200:
        return
    record.notify_state = NotifyState.Notified.value
    db.session.add(record)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return
    return
