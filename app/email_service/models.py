from datetime import datetime, timezone  # 导入处理时间的模块
from app.extensions import db
import json


class EmailNotification(db.Model):
    __tablename__ = "email_notifications"

    id = db.Column(db.Integer, primary_key=True)
    # 保存为 JSON 字符串，以支持多个收件人
    to = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # 使用可调用默认值，避免模块导入时固定时间
    pushed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        # 反序列化收件人字段
        try:
            recipients = json.loads(self.to)
        except Exception:
            recipients = [self.to]

        return {
            "id": self.id,
            "to": recipients,
            "subject": self.subject,
            "content": self.content,
            "pushed_at": self.pushed_at.isoformat(),
        }