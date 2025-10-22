# __init__.py
from flask import Flask  # 导入Flask类
# from flask_socketio import SocketIO  # 导入Flask-SocketIO扩展
from .config import Config  # 导入配置类
from .extensions import db, migrate, mail  # 导入数据库扩展

# from .auth import auth_bp    # 导入蓝图
# from .yuque import yuque_bp
# 假设您还使用 Flask-SocketIO 扩展

# 创建 Celery 实例的函数
from celery import Celery

celery = Celery()  # 全局 Celery 实例

def make_celery(app):
    """使用 Flask 配置初始化 Celery，并为任务提供应用上下文。"""
    global celery
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    # 同步 Flask 配置到 Celery
    celery.conf.update(app.config)

    # 确保所有任务在执行时都有 Flask 应用上下文（如需要使用 db、mail 等扩展）
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask

    # 将本 Celery 应用设为默认应用，保证 @shared_task 在 Web 进程中也使用该实例
    try:
        celery.set_default()
    except Exception:
        # 某些版本无需显式设置，忽略即可
        pass

    return celery

def create_app(config_class=Config):
    #  创建Flask应用实例
    app = Flask(__name__)
    
    # 加载配置（先）
    app.config.from_object(config_class)

    # 初始化数据库
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)  # 初始化邮件扩展

    # 提前初始化 Celery（在注册蓝图/导入 routes 之前），
    # 以确保 @shared_task 绑定到我们配置的 Celery 实例（使用 Redis，而非默认 AMQP）。
    make_celery(app)


    # 导入并注册主页蓝图
    from .main import main_bp
    app.register_blueprint(main_bp)

    # 导入并注册消息页面蓝图
    from .notification import notification_bp
    app.register_blueprint(notification_bp, url_prefix='/api/v1')

    # 导入并注册邮件蓝图
    from .email_service import email_bp
    app.register_blueprint(email_bp, url_prefix='/api/v1')

    # 返回应用实例
    return app