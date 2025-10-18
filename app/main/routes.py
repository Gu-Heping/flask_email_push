from . import main_bp # 导入在本模块 __init__.py 中创建的蓝图对象
from flask import render_template, request  # 导入 Flask 的渲染模板和请求对象


# 定义路由
@main_bp.route('/')
def index():
    return render_template('main/index.html', url = request.url)

@main_bp.route('/hello')
def hello():
    return "Hello, World!"

