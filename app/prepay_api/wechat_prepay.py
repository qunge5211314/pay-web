#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-21
# @Author       : HanQun
# @Introduction : 微信相关接口
# dependence

from . import prepay_api
from app import db
from app.enum import CheckType, PayType, ResponseCode, PayMode
from app.response.error import server_error, custom
from app.response.response import usually
from app.utils.wechat_utils import WeChatPrepay
from app.utils.record_utils import create_record
from app.decorators.prepay_decorator import internal_required, check_request_params, order_check, current_record


# 微信预支付接口
@prepay_api.route("/wechat", methods=["POST"])
@order_check
# @internal_required
@check_request_params(rmb=("订单金额", True, CheckType.INT),
                      title=("订单标题", True, CheckType.OTHER),
                      detail=("订单详情", False, CheckType.OTHER),
                      notify_url=("回调接口url", True, CheckType.OTHER),
                      spbill_create_ip=("客户端ip", True, CheckType.OTHER),
                      scene_info=("场景信息", False, CheckType.JSON))
def wechat_pay_prepay(**kwargs):
    if (kwargs.get("pay_type") == PayType.APPLET.value or kwargs.get("pay_type") == PayType.JSAPI.value) and (not kwargs.get("customer_id")):
        return custom(ResponseCode.PARAM_ERROR.value, "JSAPI支付必须传递用户id")
    if current_record and current_record.pay_mode == PayMode.WECHAT.value \
            and current_record.pay_type == PayType.QRCODE.value and current_record.pay_type != kwargs.get("pay_type"):
        return custom(ResponseCode.REPEAT_ORDER.value, "同一订单不可出现多种充值类型")
    elif current_record and current_record.pay_mode == PayMode.WECHAT.value \
            and current_record.pay_type in [PayType.APP.value, PayType.APPLET.value] and kwargs.get(
        "pay_type") == PayType.QRCODE.value:
        return custom(ResponseCode.REPEAT_ORDER.value, "同一订单不可出现多种充值类型")
    kwargs.update({"pay_mode": PayMode.WECHAT.value})
    record = create_record(current_record, **kwargs)
    if not record:
        return server_error()
    wechat_prepay = WeChatPrepay(record)
    if kwargs.get("pay_type") == PayType.APP.value:
        result_data = wechat_prepay.app_prepay()
    elif kwargs.get("pay_type") == PayType.APPLET.value:
        result_data = wechat_prepay.applet_prepay()
    elif kwargs.get("pay_type") == PayType.QRCODE.value:
        result_data = wechat_prepay.qrcode_prepay()
        setattr(record, "qrcode_url", result_data.get("code_url", None))
    elif kwargs.get("pay_type") == PayType.WAP.value:
        if not kwargs.get("scene_info"):
            return custom(ResponseCode.PARAM_ERROR.value, "场景信息不能为空")
        result_data = wechat_prepay.wap_prepay({"scene_info": kwargs.get("scene_info")})
        setattr(record, "qrcode_url", result_data.get("mweb_url", None))
    elif kwargs.get("pay_type") == PayType.JSAPI.value:
        result_data = wechat_prepay.jsapi_prepay({"scene_info": kwargs.get("scene_info")} if kwargs.get("scene_info") else None)
    else:
        return custom(ResponseCode.NOT_SUPPORT.value, "暂不支持其它支付方式")
    if not result_data:
        return server_error()
    record.prepay_info = result_data.get("prepayid") if result_data.get("prepayid") else None
    db.session.add(record)
    return usually("", result_data)


@prepay_api.route("/test", methods=["POST"])
def test():
    return usually("", {})
