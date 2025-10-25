# 导入蓝图
from flask import Blueprint

# 创建email_push蓝图
email_push_bp = Blueprint('email_push', __name__, template_folder='templates')

# 导入路由
from . import routes