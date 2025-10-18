from flask_sqlalchemy import SQLAlchemy  # 导入Flask-SQLAlchemy扩展
from flask_migrate import Migrate  # 导入Flask-Migrate扩展
from flask_mailing import Mail

db = SQLAlchemy()  # 创建SQLAlchemy数据库对象
migrate = Migrate()  # 创建Migrate对象，用于数据库迁移
mail = Mail()  # 创建Mail对象，用于发送邮件

