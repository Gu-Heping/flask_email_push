# 导入FlaskForm基类和表单字段、验证器
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Email, DataRequired
from wtforms import StringField, EmailField, SubmitField, TextAreaField

# 创建发送邮件表单类
class EmailForm(FlaskForm):
    to = EmailField('收件邮箱', validators=[DataRequired(message='不能为空'), Email(message='请输入有效的邮箱地址')])
    subject = StringField('主题（标题）', validators=[DataRequired(message='不能为空')])
    content = TextAreaField('内容', validators=[DataRequired(message='不能为空')])
    submit = SubmitField('发送邮件', id="submit-btn")  # 添加id属性以便JavaScript使用