#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-26
# @Author       : HanQun
# @Introduction : 订单记录相关工具
# dependence
# 创建支付记录方法
from app import db
from app.models import PayRecord


def create_record(current_record, **data):
    if current_record:
        db.session.delete(current_record)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            return None
    new_record = PayRecord(
        pay_mode=data.get("pay_mode"),
        pay_type=data.get("pay_type"),
        out_trade_no=data.get("out_trade_no"),
        rmb=data.get("rmb"),
        title=data.get("title"),
        detail=data.get("detail"),
        invalid_time=data.get("invalid_time"),
        customer_id=data.get("customer_id"),
        spbill_create_ip=data.get("spbill_create_ip"),
        sign_type="MD5" if data.get("pay_mode") == 0 else "RSA2",
        notify_url=data.get("notify_url")
    )
    db.session.add(new_record)
    return new_record