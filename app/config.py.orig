import os  # 读写文件
from dotenv import load_dotenv  # 用来加载.env文件

# 加载环境变量
load_dotenv()
# 这时 .env 中的内容被读取到 os.environ 字典中

# 获取当前文件的绝对路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:  # 设置基础配置
    
    # copilot写的很健壮的设置布尔模式的代码
    DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")  # 是否开启调试模式，默认关闭

    # 数据库配置，使用 SQLite 数据库，数据库文件位于 app 目录
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭对象修改追踪，提高性能

    # 邮件配置
    MAIL_SERVER = 'smtp.126.com'  # SMTP 服务器地址
    MAIL_PORT = 465  # SMTP 端口
    MAIL_USERNAME = 'peace0824@126.com'  # 邮箱用户名
    MAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")  # 邮箱授权码，从环境变量中读取  # 邮箱密码
    MAIL_USE_TLS = False  # 是否使用 TLS
    MAIL_USE_SSL = True  # 是否使用 SSL
    MAIL_DEFAULT_SENDER = 'peace0824@126.com'  # 默认发件人

    # Celery 配置
    CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Redis 作为消息队列
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # 结果存储

    # 显式指定 Celery 任务模块，避免混用新旧格式
    CELERY_INCLUDE = [
        "app.tasks.email_tasks",
        "app.tasks.other_tasks"
    ]

    # 推送签名配置（用于 Webhook/Email 接口签名校验）
    # 使用环境变量设置，例如：PUSH_SIGNING_SECRET=mysecret
    PUSH_SIGNING_SECRET = os.environ.get("PUSH_SIGNING_SECRET", "")
    # 可选：签名时间戳允许的偏差（秒），用于防重放攻击
    PUSH_SIGNATURE_TOLERANCE = int(os.environ.get("PUSH_SIGNATURE_TOLERANCE", 300))

    # SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭对象修改追踪，提高性能

    