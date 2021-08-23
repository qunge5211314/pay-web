#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-27
# @Author       : HanQun
# @Introduction : 订单查询接口
# dependence
from app.decorators.prepay_decorator import check_request_params, internal_required
from app.enum import CheckType, ResponseCode
from app.models import PayRecord
from app.response import succeed
from app.response.error import custom
from . import order_query


@order_query.route("/query", methods=["GET"])
@internal_required
@check_request_params(out_trade_no=("订单号", True, CheckType.OTHER))
def order_query(**kwargs):
    current_record = PayRecord.query.filter(PayRecord.out_trade_no == kwargs.get("out_trade_no")).first()
    if not current_record:
        return custom(ResponseCode.NOT_FOUND.value, "未查询到该订单")
    return succeed("", current_record.to_json())