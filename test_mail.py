from flask import Flask
from flask_mailing import Mail, Message
import os
import asyncio

app = Flask(__name__)
app.config["MAIL_SERVER"] = "smtp.126.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "peace0824@126.com"
app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_DEFAULT_SENDER"] = "peace0824@126.com"

mail = Mail(app)

async def send_test_mail():
    with app.app_context():
        message = Message(
            subject="测试邮件",
            recipients=["1179350197@qq.com"],
            body="这是一封测试邮件。"
        )
        print("准备发送:", message)
        await mail.send_message(message)
        print("邮件已发送")

if __name__ == "__main__":
    asyncio.run(send_test_mail())