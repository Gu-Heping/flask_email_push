  # 导入发送邮件的函数
from . import email_bp # 导入在本模块 __init__.py 中创建的蓝图对象
from flask import request, jsonify, current_app  # 精简导入
from flask_restful import Api  # 仅用于绑定在蓝图（当前路由使用函数风格）
from werkzeug.exceptions import BadRequest
import hashlib
import hmac
import time
from datetime import datetime, timezone  # 导入处理时间的模块
from flask_restful import Resource, Api, reqparse, inputs  # 导入 Flask-RESTful 的资源和 API 类以及请求解析器
from app.extensions import db  # 导入数据库对象

from app.tasks.email_tasks import send_email  # 导入邮件任务
from .models import EmailNotification  # 导入 EmailNotification 模型

# 初始化 Flask-RESTful 的 API 对象，并传入蓝图对象
# 注意：API 是绑定到蓝图 (email_bp) 上的
api = Api(email_bp)

# 获取当前UTC时间的函数
def get_current_utc():
    return datetime.now(timezone.utc)

@email_bp.route('/get/email', methods=['GET'])
def get_email():
    """
    获取所有邮件通知接口
    GET /api/v1/get/email
    """
    notifications = EmailNotification.query.all()
    return jsonify([n.to_dict() for n in notifications]), 200 

@email_bp.route('/push/email', methods=['POST'])
def push_email():
  """
  邮件推送接口
  POST /api/v1/push/email
  Headers:
    Content-Type: application/json
    X-Signature: sha256=<hex>   （可选，若配置 PUSH_SIGNING_SECRET 则强制校验）
    X-Timestamp: <epoch-seconds>（可选，签名时用于防重放）
  Body:
    {
    "to": ["a@x.com", "b@x.com"] | "a@x.com",
    "subject": "标题",
    "content": "正文"
    }
  """
  if not request.is_json:
    raise BadRequest("Content-Type 必须为 application/json")

  data = request.get_json(silent=True) or {}
  to = data.get('to')
  subject = data.get('subject')
  content = data.get('content')

  # 参数校验
  if not to or not subject or not content:
    return jsonify({
      "code": "INVALID_PARAMS",
      "message": "必须提供 to/subject/content"
    }), 400

  # 规范化收件人列表
  recipients = to if isinstance(to, list) else [to]
  recipients = [r for r in recipients if isinstance(r, str) and r.strip()]
  if not recipients:
    return jsonify({"code": "INVALID_PARAMS", "message": "收件人列表无效"}), 400

  # 签名校验（若配置了密钥则生效）
  secret = (current_app.config.get('PUSH_SIGNING_SECRET') or '').encode('utf-8')
  if secret:
    req_sig = request.headers.get('X-Signature', '')
    ts = request.headers.get('X-Timestamp')
    if not req_sig or not ts:
      return jsonify({"code": "UNAUTHORIZED", "message": "缺少签名或时间戳"}), 401
    try:
      ts = int(ts)
    except ValueError:
      return jsonify({"code": "UNAUTHORIZED", "message": "时间戳格式错误"}), 401
    # 时间窗口校验
    tol = int(current_app.config.get('PUSH_SIGNATURE_TOLERANCE', 300))
    if abs(int(time.time()) - ts) > tol:
      return jsonify({"code": "UNAUTHORIZED", "message": "请求已过期"}), 401
    # 签名串：timestamp + '.' + body
    body_raw = request.get_data()  # 原始字节
    base = f"{ts}.".encode('utf-8') + body_raw
    digest = hmac.new(secret, base, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(req_sig.replace('sha256=', ''), digest):
      return jsonify({"code": "UNAUTHORIZED", "message": "签名校验失败"}), 401

  pushed_at = get_current_utc()
  # 序列化收件人列表为 JSON 字符串以存储
  import json
  notif = EmailNotification(subject=subject, to=json.dumps(recipients, ensure_ascii=False), content=content, pushed_at=pushed_at)
  db.session.add(notif)
  db.session.commit()

  # 入队 Celery 任务
  async_result = send_email.delay(subject=subject, recipients=recipients, body=content)

  return jsonify({
    "code": "ACCEPTED",
    "message": "邮件发送已入队",
    "task_id": async_result.id,
    "to": recipients
  }), 202
