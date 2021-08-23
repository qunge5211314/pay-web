#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-23
# @Author       : HanQun
# @Introduction : 定时任务
# dependence
from app.enum import PayState, NotifyState
from app.models import PayRecord
from .callback_utils import callback_function
from app import db


# 未通知的记录处理定时任务
def unnotify_record_handle():
    print("unnotify_record_handle")
    with db.app.app_context():
        records = PayRecord.query.filter(PayRecord.pay_state != PayState.WAITING.value,
                                         PayRecord.notify_state == NotifyState.WAITING.value).all()
        for record in records:
            callback_function(record)
