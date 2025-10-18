# notification/routes.py
from . import notification_bp # 导入在本模块 __init__.py 中创建的蓝图对象
from flask import render_template, request  # 导入 Flask 的渲染模板和请求对象
from flask_restful import Resource, Api, reqparse, inputs  # 导入 Flask-RESTful 的资源和 API 类以及请求解析器
from datetime import datetime, timezone  # 导入处理时间的模块
from app.extensions import db  # 导入数据库对象
from .models import Notification  # 导入 Notification 模型

from app.tasks.email_tasks import send_email  # 导入发送邮件的函数

# 初始化 Flask-RESTful 的 API 对象，并传入蓝图对象
# 注意：API 是绑定到蓝图 (notification_bp) 上的
api = Api(notification_bp)

# 获取当前UTC时间的函数
def get_current_utc():
    return datetime.now(timezone.utc)

# 定义请求解析器
parser = reqparse.RequestParser()

parser.add_argument(
    'title',
    type=str,
    required=True,
    help='标题不能为空'
)

parser.add_argument(
    'content',
    type=str,
    required=True,
    help='内容不能为空'
)

parser.add_argument(
    'pushed_at',
    type=inputs.datetime_from_iso8601,
    default=get_current_utc,  # 现在返回 datetime
    required=False,
    help='推送时间 (ISO 8601 格式)。如果未提供，默认为当前 UTC 时间。'
)


# 定义 NotificationList 资源（处理 /api/v1/notifications 的 POST 和 GET）
class NotificationListResource(Resource):
    
    def get(self):
        notifications = Notification.query.all()
        return [n.to_dict() for n in notifications], 200

    def post(self):
        args = parser.parse_args()
        title = args['title']
        content = args['content']
        pushed_at = args['pushed_at']
        # TODO 处理数据，完善数据信息

        notif = Notification(title=title, content=content, pushed_at=pushed_at)
        db.session.add(notif)
        db.session.commit()

        send_email.delay(
            subject=f"新通知: {title}",
            recipients=['1179350197@qq.com'],
            body=f"您有新的通知: {content}"
        )

        return notif.to_dict(), 201

api.add_resource(NotificationListResource, '/notifications')


# 定义接受信息的路由
# @notification_bp.route('/' , methods=['POST', 'GET'])
# def index():
#     # 处理通知页面的逻辑
#     if request.method == 'POST':
#         # 接受通知数据
#         if not request.is_json:
#             return {"error": "只接受 JSON 数据"}, 400
#         data = request.get_json()
#         try:
#             # TODO 处理数据，完善数据信息
#             content = data['content']
#             return {"message": f"收到通知: {content}"}, 200
            
#         except KeyError as e:
#             # 捕获如果关键字段缺失的错误
#             return {"error": f"缺少必需字段: {e}"}, 400

#     elif request.method == 'GET':
#         return "<p>这是通知接口</p>"  # 返回接口页面

# @notification_bp.route('/status', methods=['GET'])
# def status():
#     return {"status": "success", "message": "Notification service is running."}, 200