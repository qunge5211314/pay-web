#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-21
# @Author       : HanQun
# @Introduction : 微信支付工具类
# dependence
import hashlib
import requests
import xmltodict
import time
from random import choice

from app import db
from app.enum import PayType
from app.models import PayRecord
from xml.etree import ElementTree


class WeChatBase(object):
    # 获取随机字符串方法
    def get_nonce_str(self, length=32):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        str_list = [choice(chars) for i in range(length)]
        return "".join(str_list)

    # xml转换成字典方法
    def xml_to_dict(self, xml):
        data = xmltodict.parse(xml)
        return dict(data)

    # 特殊xml转字典方法
    def special_xml_to_dict(self, xml):
        data = dict()
        root = ElementTree.fromstring(xml)
        for child in root:
            value = child.text
            data[child.tag] = value
        return data

    # 字典转换成xml方法
    def dict_to_xml(self, **data):
        xml = "<xml>"
        for key, value in data.items():
            if value:
                xml = xml + '<' + key + '>' + str(value) + '</' + key + '>'
        xml = xml + "</xml>"
        return xml.encode("utf-8")

    # 字典数据转换成url方法
    def dict_to_url(self, **data):
        buff = ["{0}={1}".format(key, data.get(key)) for key in sorted(data) if data.get(key)]
        return "&".join(buff)

    # 获取签名方法
    def get_sign(self, **data):
        from app.constant.wechat_constant import API_KEY
        temp_string = self.dict_to_url(**data)
        temp_string = temp_string + "&key=" + API_KEY
        m = hashlib.md5()
        m.update(temp_string.encode('utf-8'))
        sign = m.hexdigest().upper()
        return sign


class WeChatPrepay(WeChatBase):
    def __init__(self, pay_record):
        from app.constant.wechat_constant import NOTIFY_URL
        self.__pay_record = pay_record
        self.__params = {
            'appid': self.get_trade_type()[1],
            'mch_id': self.get_trade_type()[2],
            'nonce_str': self.get_nonce_str(),
            'body': pay_record.title,
            'detail': pay_record.detail,
            'out_trade_no': pay_record.out_trade_no,
            'total_fee': pay_record.rmb,
            'trade_type': self.get_trade_type()[0],
            'notify_url': NOTIFY_URL,
            'time_expire': pay_record.invalid_time.strftime("%Y%m%d%H%M%S") if pay_record.invalid_time else "",
            'openid': pay_record.customer_id,
            'sign_type': 'MD5'
        }

    # 根据支付类型返回相应微信交易类型参数
    def get_trade_type(self):
        from app.constant.wechat_constant import APP_ID, APPLET_ID, \
            APP_MCH_ID, APPLET_MCH_ID, H5_APP_ID, H5_MCH_ID, JSAPI_APP_ID, JSAPI_MCH_ID
        if self.get_pay_record().pay_type == PayType.APP.value:
            return "APP", APP_ID, APP_MCH_ID
        elif self.get_pay_record().pay_type == PayType.APPLET.value:
            return "JSAPI", APPLET_ID, APPLET_MCH_ID
        elif self.get_pay_record().pay_type == PayType.QRCODE.value:
            return "NATIVE", APP_ID, APP_MCH_ID
        elif self.get_pay_record().pay_type == PayType.WAP.value:
            return "MWEB", H5_APP_ID, H5_MCH_ID
        elif self.get_pay_record().pay_type == PayType.JSAPI.value:
            return "JSAPI", JSAPI_APP_ID, JSAPI_MCH_ID
        else:
            return "", "", ""

    def update_param(self, **kwargs):
        self.__params.update(kwargs)

    def get_response_dict(self, scene_info=None):
        from app.constant.wechat_constant import PREPAY_URL
        if self.get_pay_record().pay_type == PayType.WAP.value or self.get_pay_record().pay_type == PayType.JSAPI.value:
            if scene_info:
                self.update_param(**scene_info)
        self.update_param(**{"sign": self.get_sign(**self.get_param())})
        xml = self.dict_to_xml(**self.get_param())
        response = requests.post(PREPAY_URL, xml, headers={'Content-Type': 'application/xml'})
        try:
            response.raise_for_status()
        except Exception as e:
            print(e)
            return {}
        response_xml = response.text.encode('ISO-8859-1').decode('utf-8')
        response_dict = self.xml_to_dict(response_xml)
        print(response_dict)
        return response_dict

    def get_param(self):
        return self.__params

    def get_pay_record(self):
        return self.__pay_record

    # app支付方法，返回app支付所需参数
    def app_prepay(self):
        response_dict = self.get_response_dict()
        if response_dict.get('xml', {}).get('return_code', "FAIL") == 'SUCCESS':
            if response_dict.get('xml', {}).get('result_code') == 'SUCCESS':
                info = {
                    'appid': self.get_param().get('appid'),
                    'partnerid': self.get_param().get('mch_id'),
                    'prepayid': response_dict.get('xml').get('prepay_id'),
                    'package': "Sign=WXPay",
                    'noncestr': self.get_param().get('nonce_str'),
                    'timestamp': str(int(time.time()))}
                info.update({"sigin": self.get_sign(**info)})
                return info
            else:
                return {}
        else:
            return {}

    # 小程序支付方法，返回小程序支付所需参数
    def applet_prepay(self):
        response_dict = self.get_response_dict()
        if response_dict.get('xml', {}).get('return_code', "FAIL") == 'SUCCESS':
            if response_dict.get('xml', {}).get('result_code') == 'SUCCESS':
                info = {
                    'appId': self.get_param().get('appid'),
                    'package': "prepay_id={}".format(response_dict.get('xml').get('prepay_id')),
                    'nonceStr': self.get_param().get('nonce_str'),
                    'timeStamp': str(int(time.time())),
                    'signType': self.get_param().get('sign_type')}
                info.update({"paySign": self.get_sign(**info)})
                return info
            else:
                return {}
        else:
            return {}

    # 二维码支付方法，返回二维码支付所需数据
    def qrcode_prepay(self):
        response_dict = self.get_response_dict()
        if response_dict.get('xml', {}).get('return_code', "FAIL") == 'SUCCESS':
            if response_dict.get('xml', {}).get('result_code') == 'SUCCESS':
                info = {
                    'prepayid': response_dict.get('xml').get('prepay_id'),
                    'code_url': response_dict.get('xml').get('code_url')}
                return info
            else:
                return {}
        else:
            return {}

    # 手机网页支付方法，返回二维码支付所需数据
    def wap_prepay(self, scene_info):
        response_dict = self.get_response_dict(scene_info)
        print(response_dict)
        if response_dict.get('xml', {}).get('return_code', "FAIL") == 'SUCCESS':
            if response_dict.get('xml', {}).get('result_code') == 'SUCCESS':
                info = {
                    'prepayid': response_dict.get('xml').get('prepay_id'),
                    'mweb_url': response_dict.get('xml').get('mweb_url')}
                return info
            else:
                return {}
        else:
            return {}

    # 公众号支付方法，返回二维码支付所需数据
    def jsapi_prepay(self, scene_info):
        response_dict = self.get_response_dict(scene_info)
        print(response_dict)
        if response_dict.get('xml', {}).get('return_code', "FAIL") == 'SUCCESS':
            if response_dict.get('xml', {}).get('result_code') == 'SUCCESS':
                info = {
                    'appId': self.get_param().get('appid'),
                    'package': "prepay_id={}".format(response_dict.get('xml').get('prepay_id')),
                    'nonceStr': self.get_param().get('nonce_str'),
                    'timeStamp': str(int(time.time())),
                    'signType': self.get_param().get('sign_type')}
                info.update({"paySign": self.get_sign(**info)})
                return info
            else:
                return {}
        else:
            return {}


class WeChatNotify(WeChatBase):
    def __init__(self, xml):
        self.__xml = xml

    def get_xml(self):
        return self.__xml

    def return_data(self, state, msg):
        return "<xml><return_code><![CDATA[{state}]]></return_code><return_msg><![CDATA[{msg}]></return_msg></xml>".format(
            state=state, msg=msg)

    def check_sign(self, **data):
        wechat_sign = data.pop("sign") if "sign" in data.keys() else ""
        temp_sign = self.get_sign(**data)
        if wechat_sign == temp_sign:
            return True
        else:
            return False
