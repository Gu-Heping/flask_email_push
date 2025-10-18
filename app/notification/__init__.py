# 导入蓝图
from flask import Blueprint

# 创建main蓝图，作为主页
notification_bp = Blueprint('notification', __name__, template_folder='templates')  # template_folder='templates'指定模板在子文件夹下

# 导入路由
from . import routes

