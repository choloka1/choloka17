from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegisterForm(FlaskForm):
    name = StringField('სახელი', validators=[DataRequired()])
    surname = StringField('გვარი', validators=[DataRequired()])
    email = StringField('ელფოსტა', validators=[DataRequired(), Email()])
    password = PasswordField('პაროლი', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('გაიმეორე პაროლი', validators=[
        DataRequired(), EqualTo('password', message='პაროლები არ ემთხვევა')
    ])
    submit = SubmitField('რეგისტრაცია')


class ForgotForm(FlaskForm):
    email = StringField('ელფოსტა', validators=[DataRequired(), Email()])
    submit = SubmitField('პაროლის აღდგენა')
