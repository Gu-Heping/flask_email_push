# 导入蓝图
from flask import Blueprint

# 创建email蓝图，作为邮件相关功能的入口
email_bp = Blueprint('email', __name__)  # template_folder='templates'指定模板在子文件夹下

# 导入路由
from . import routes

from flask_mailing import Message
from app.extensions import mail

# 封装邮件发送逻辑
async def send_email(subject, recipients, body):
    message = Message(
        subject=subject,
        recipients=recipients,
        body=body,
    )
    await mail.send_message(message)
