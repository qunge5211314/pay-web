#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-21
# @Author       : HanQun
# @Introduction : 支付记录相关model
# dependence
from app import db
from .base_model import BaseModel


class PayRecord(BaseModel):
    __tablename__ = "pay_record"
    pay_mode = db.Column(db.SmallInteger, default=0, index=True, comment='支付方式')  # 支付方式 0：微信 1：支付宝 2：苹果
    pay_type = db.Column(db.SmallInteger, default=0, index=True, comment='支付类型')  # 支付类型 0：app 1：小程序 2：二维码
    pay_state = db.Column(db.SmallInteger, default=0, index=True, comment='支付状态')  # 支付状态 0：待支付 1：支付完成 2：支付失败
    out_trade_no = db.Column(db.String(64), index=True, nullable=False, unique=True, comment='打卡助手订单号')  # 打卡助手订单号
    rmb = db.Column(db.Integer, default=0, index=True, nullable=False, comment='人民币总额')  # 人民币总额  单位：分
    title = db.Column(db.String(256), nullable=False, index=True, comment='订单标题')  # 订单标题
    detail = db.Column(db.String(800), index=True, comment='商品描述详情')  # 商品描述详情
    invalid_time = db.Column(db.DateTime, index=True, comment='支付失效时间')  # 支付失效时间 对应于微信time_expire 支付宝timeout_express
    customer_id = db.Column(db.String(64), index=True, comment='特殊支付下用户id')  # 特殊支付下用户id 对应于微信open_id 支付宝buyer_id
    sign_type = db.Column(db.String(64), index=True, comment='签名类型')  # 签名类型
    spbill_create_ip = db.Column(db.String(100), index=True, comment='支付终端ip')  # 支付终端ip
    prepay_info = db.Column(db.String(800), index=True, comment='第三方预支付交易码')  # 第三方预支付交易码
    qrcode_url = db.Column(db.String(800), index=True, comment='第三方支付二维码url')  # 第三方支付二维码url
    notify_url = db.Column(db.String(500), index=True, nullable=False, comment='回调url')  # 回调url 用于通知打卡助手业务
    notify_state = db.Column(db.SmallInteger, default=0, index=True, comment='回调通知状态')  # 回调通知状态 0未通知 1已通知
    trade_no = db.Column(db.String(64), index=True, comment='微信支付宝交易订单号')  # 微信支付宝交易订单号 对应于微信transaction_id 支付宝trade_no
    result = db.Column(db.String(100), index=True, comment='支付结果回调信息码')  # 支付结果回调信息码 对应于微信return_code 支付宝resultStatus
    total_fee = db.Column(db.Integer, index=True, comment='微信支付宝回调时返回的订单总金额')  # 微信支付宝回调时返回的订单总金额 对应于微信total_fee 支付宝total_amount 单位：分
    receipt_fee = db.Column(db.Integer, index=True, comment='支付实收金额')  # 支付实收金额 对应于微信cash_fee 支付宝receipt_amount 单位：分
    pay_time = db.Column(db.DateTime, index=True, comment='支付时间')  # 支付时间 对应于微信time_end 支付宝gmt_payment
    pay_channel = db.Column(db.String(100), index=True, comment='支付渠道信息')  # 支付渠道信息 对应于微信bank_type 支付宝fund_bill_list
