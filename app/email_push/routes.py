from . import email_push_bp # 导入在本模块 __init__.py 中创建的蓝图对象
from flask import render_template, request  # 导入 Flask 的渲染模板和请求对象
from app.email_push.models import EmailForm  # 导入表单类
from flask import jsonify  # 导入 jsonify 用于返回 JSON 响应

# 定义路由，展示邮件发送页面
@email_push_bp.route('/')
def index():
    # 为表单赋值
    form = EmailForm()
    return render_template('email_push/index.html', url = request.url, form=form)

# 定义路由，处理表单提交
@email_push_bp.route('/submit_data', methods=['POST'])
def submit_data():
    form = EmailForm()
    if form.validate_on_submit():
        # 这里处理表单数据，例如保存到数据库
        email = form.email.data
        subject = form.subject.data
        body = form.body.data
        print(f"收到推送信息：邮箱='{email}', 主题='{subject}', 内容='{body}'")
        
        # 返回一个成功的JSON响应
        return jsonify({'success': True, 'message': '信息推送成功！'})
    
    # 如果验证失败，返回一个包含错误的JSON响应
    return jsonify({'success': False, 'errors': form.errors})