from flask import Blueprint

notify_api = Blueprint("notify_api", __name__)

from . import wechat_notify, alipay_notify