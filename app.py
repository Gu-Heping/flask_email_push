# 使用env文件
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# flask后端
from flask import Flask, request, jsonify, render_template
import json # 用于处理JSON数据
from pywebpush import webpush # 用来处理VAPID密钥和发送推送

# 导入SocketIO和emit
from flask_socketio import SocketIO, emit

# 用于发送邮件的库
import smtplib
from email.mime.text import MIMEText

# 用来发邮件的账号
sender_email = "peace0824@126.com"
# 邮箱授权码
sender_password = os.getenv("EMAIL_PASSWORD")
# 测试收件人邮箱
test_recipient_email = "1179350197@qq.com"

# 发送邮件的函数
def send_email(to_email, subject, body):
    # subject为标题，body为正文
    message = MIMEText(body, 'plain', 'utf-8')
    message['From'] = sender_email
    message['To'] = to_email
    message['Subject'] = subject

    try:
        # 创建SMTP对象，连接到126邮箱的SMTP服务器
        server = smtplib.SMTP('smtp.126.com', 25)
        # 登录发件人邮箱
        server.login(sender_email, sender_password)
        # 发送邮件
        server.sendmail(sender_email, to_email, message.as_string())
        print("邮件发送成功")
        # 关闭连接
        server.quit()
    except smtplib.SMTPException as e:
        print("Error: 无法发送邮件", e)

app = Flask(__name__)

'''
------------------------------------------------------------------
Flask后端代码，处理Web推送订阅和发送
'''

# VAPID密钥对
VAPID_PUBLIC_KEY = "BGrRUrmaLOIyUyV5asT44vvQOLvVFkLzULH2aNR4MJ7jcL4SE2BKm2KY1BHb8hQSDCBZg_hROufVuJxE1f3DGZ4"
VAPID_PRIVATE_KEY = "jGgKTZoZ3qecyKHkNNB1OQ_aiA09886NnwAW3UhUoy0"  # 私钥就放这了，反正web推送已经用不了了
VAPID_CLAIM_EMAIL = 'mailto:yue76093219@126.com'

# 存储订阅信息的列表
subscriptions = []

@app.route('/')
def index():
    return render_template('index.html', vapid_public_key=VAPID_PUBLIC_KEY)


@app.route('/api/v1/subscribe', methods=['POST'])
def handle_subscription():
    # 获取JSON数据
    subscription_data = request.get_json()

    # 进行验证
    if not subscription_data or 'endpoint' not in subscription_data:
        return jsonify({"error": "数据格式不正确，缺少endpoint"}), 400
    
    # 存储订阅信息
    subscriptions.append(subscription_data)
    print(f"\n[Flask后端]：成功收到新订阅地址。当前订阅总数：{len(subscriptions)}\n")

    # 返回成功响应
    return jsonify({"status": "订阅成功"}), 201

#测试是否联通
@app.route('/api/v1/push', methods=['POST'])
def handle_push():
    if not subscriptions:  # 检查是否有订阅
        return jsonify({"error": "没有订阅"}), 400
    
    # 发送测试消息
    payload = {
        "title": "😘测试成功！",
        "body": "这是来自Flask后端的一个测试推送消息，peace历经千辛万苦成功了",
    }

    # 初始化订阅数量
    sent_count = 0

    for subscription_info in subscriptions:  # 遍历订阅列表
        try:
            # 使用webpush发送推送消息
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),  # 将payload转换为JSON字符串
                vapid_private_key=VAPID_PRIVATE_KEY,  # 用私钥进行签名
                vapid_claims={"sub": VAPID_CLAIM_EMAIL}  # 声明
            )
            sent_count += 1  # 成功发送后，计数加1
        
        except Exception as e:  # 捕获异常
            print(f"推送失败到{subscription_info['endpoint']}: {e}")
            # TODO:删除无效的订阅
    
    return jsonify({
        "status": "推送完成",
        "total_subscriptions": len(subscriptions),
        "message_sent": sent_count
    }), 200

'''
-------------------------------------------------------------
SocketIO代码
'''
# 初始化SocketIO
# 注意：这里的cors_allowed_origins设置为'*'，允许所有来源连接
socketio = SocketIO(app, cors_allowed_origins='*')

# 定义SocketIO事件处理
@socketio.on('connect')
def handle_connect():
    print('='*50)
    print(f"SocketIO客服端链接成功！Session ID: {request.sid}")
    print('='*50)
    send_email(test_recipient_email, "WebSocket连接成功", f"客户端已连接，Session ID: {request.sid}")

    # 当客户端连接时，发送一条欢饮消息
    emit('server_response', {'data': '连接成功！可以接收实时通知'})

# 处理客户端断开连接事件
@socketio.on('disconnect')
def handle_disconnect():
    print(f"SocketIO 客户端断开连接。Session ID: {request.sid}")

# 处理客户端发送的测试消息
@socketio.on('test_message')
def handle_test_message(data):
    # 接收前端发送的消息
    print(f"<- 收到来自前端 ({request.sid}) 的消息： {data['message']}")

    # 立即向所有链接的客户端推送一条实时通知
    # broadcast=True 表示向所有客户端发送，否则只发送给当前客户端
    socketio.emit('server_response', {'data': '实时通知：后端已收到你的请求！'})
    print("-> 向所有客户端发送实时通知")

# 处理客户端发送的自定义消息
@socketio.on('message')
def handle_message(data):
    # 接收前端发送的消息
    print(f"<- 收到来自前端 ({request.sid}) 的消息： {data['message']}")
    send_email(test_recipient_email, "WebSocket消息", f"收到来自客户端 ({request.sid}) 的消息：{data['message']}")
    # 立即向所有链接的客户端推送一条实时通知
    socketio.emit('server_response', {'data': f'实时通知：后端已收到你的消息：{data["message"]}'})
    print("-> 向所有客户端发送实时通知")

# 替换运行方式
if __name__ == '__main__':
    # Flask后端运行
    # 允许在本地调试
    # app.run(debug=False, host='0.0.0.0')

    # 使用SocketIO运行
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)