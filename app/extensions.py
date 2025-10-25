# 导入Flask-SQLAlchemy扩展
from flask_sqlalchemy import SQLAlchemy

# 导入Flask-Migrate扩展
from flask_migrate import Migrate

# 导入Flask-Mailing扩展
from flask_mailing import Mail

# 导入Flask-Bootstrap5扩展
from flask_bootstrap import Bootstrap5

# 导入Flask-WTF扩展（如果需要表单支持）
from flask_wtf import CSRFProtect

db = SQLAlchemy()  # 创建SQLAlchemy数据库对象
migrate = Migrate()  # 创建Migrate对象，用于数据库迁移
mail = Mail()  # 创建Mail对象，用于发送邮件
bootstrap = Bootstrap5()  # 创建Bootstrap5对象，用于前端样式
csrf = CSRFProtect()  # 创建CSRFProtect对象，用于防止CSRF攻击
