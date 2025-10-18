# notification/models.py
from flask_sqlalchemy import SQLAlchemy  # 导入 SQLAlchemy
from datetime import datetime, timezone  # 导入处理时间的模块
from app.extensions import db

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    pushed_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "pushed_at": self.pushed_at.isoformat(),
        }