#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-27
# @Author       : HanQun
# @Introduction : 苹果支付预支付接口
# dependence
# 苹果支付验证接口
from app import db
from app.decorators.prepay_decorator import internal_required, check_request_params, current_record, order_check
from app.enum import CheckType, PayMode
from app.response import succeed, usually
from app.utils.record_utils import create_record
from . import prepay_api


@prepay_api.route("/appstore/prepay", methods=["POST"])
@order_check
@internal_required
@check_request_params(rmb=("订单金额", True, CheckType.INT),
                      title=("订单标题", True, CheckType.OTHER),
                      detail=("订单详情", False, CheckType.OTHER),
                      notify_url=("回调接口url", True, CheckType.OTHER),
                      spbill_create_ip=("客户端ip", False, CheckType.OTHER))
def appstore_check(**kwargs):
    kwargs.update({"pay_mode": PayMode.APPLE.value})
    record = create_record(current_record, **kwargs)
    db.session.add(record)
    return usually("记录成功")