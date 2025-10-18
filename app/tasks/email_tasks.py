from flask_mailing import Message
from app.extensions import mail
from celery import shared_task
from flask import current_app
import asyncio
import json
import traceback
from typing import List, Optional


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,           # 指数退避：1s, 2s, 4s, ...（叠加抖动）
    retry_backoff_max=60,         # 最大退避 60s
    retry_jitter=True,            # 加抖动，避免惊群
    max_retries=5,                # 最多重试 5 次
    default_retry_delay=5,        # 基础延迟（部分 broker 需要）
)
def send_email(self, subject: str, recipients: List[str], body: str, html: Optional[str] = None):
    """发送邮件的 Celery 异步任务（带自动重试与简易 DLQ）

    Args:
        subject: 邮件标题
        recipients: 收件人列表
        body: 纯文本正文
        html: 可选的 HTML 正文
    Behavior:
        - 失败自动重试，指数退避，最多 5 次
        - 达到最大重试后，推入简易 DLQ（Redis list 或日志记录）
    """
    try:
        message = Message(
            subject=subject,
            recipients=recipients,
            body=body,
            html=html,
        )
        with current_app.app_context():
            asyncio.run(mail.send_message(message))
        print(f"邮件已发送到: {', '.join(recipients)}")
        return {"status": "sent", "recipients": recipients}

    except Exception as exc:  # noqa: BLE001 - 记录所有异常并重试
        # 若可继续重试，交给 Celery 自带的 retry 机制
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            # 达到最大重试：写入简易 DLQ（这里以日志/控制台为例；也可以写入 Redis/List）
            payload = {
                "subject": subject,
                "recipients": recipients,
                "body": body[:2000],  # 避免过长
                "error": str(exc),
                "trace": traceback.format_exc(limit=3),
            }
            try:
                # 简单示例：打印到控制台。可替换为 Redis list: r.lpush('dlq:email', json.dumps(payload))
                print("[DLQ][email]", json.dumps(payload, ensure_ascii=False))
            except Exception:
                pass
            # 将异常继续抛出，以便可观测平台/日志系统捕获
            raise