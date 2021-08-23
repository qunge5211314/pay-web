#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-26
# @Author       : HanQun
# @Introduction : 支付宝支付工具
# dependence
import base64

from Cryptodome.Hash import MD5, SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5
from alipay import AliPay



class AliPaySub(AliPay):
    def verify(self, data, signature):
        sign_type = data.pop("sign_type", "RSA")
        if sign_type == "RSA":
            return super(AliPaySub, self).verify(data, signature)
        else:
            unsigned_items = self._ordered_data(data)
            message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
            signer = PKCS1_v1_5.new(self.app_private_key)
            digest = SHA256.new()
            digest.update(message.encode("utf8"))
            print(signer.sign(digest))
            print()
            if signer.verify(digest, base64.decodebytes(signature.encode("utf8"))):
                return True
            return False



