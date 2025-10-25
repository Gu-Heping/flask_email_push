from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired

class EmailForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    body = StringField('Body', validators=[DataRequired()])
    submit = SubmitField('Send Email', )