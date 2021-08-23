#!python3.6
# _*_ coding:utf-8 _*_
#
# @Version      : 1.0
# @Date         : 2019-08-21
# @Author       : HanQun
# @Introduction : 打卡助手支付服务主启动管理模块
# dependence
import os
from app import create_app, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from raven.contrib.flask import Sentry

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

sentry = Sentry(app, dsn=app.config['SENTRY_DSN'])
app.sentry = sentry


def make_shell_context():
    return dict(app=app, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def unnotify_record_handle():
    print("unnotify_record_handle")
    from app.models import PayRecord
    from app.enum import PayState, NotifyState
    from app.utils.callback_utils import callback_function
    with db.app.app_context():
        records = PayRecord.query.filter(PayRecord.pay_state != PayState.WAITING.value,
                                         PayRecord.notify_state == NotifyState.WAITING.value).all()
        for record in records:
            callback_function(record)


if __name__ == '__main__':
    manager.run()
