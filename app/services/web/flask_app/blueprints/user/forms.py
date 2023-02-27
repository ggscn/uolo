from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo
from wtforms_components import EmailField, Email
from wtforms_alchemy import Unique, ModelForm

from flask_app.blueprints.user.models import User, db

class NewUserForm(FlaskForm, ModelForm):
    email_validators = [
        DataRequired(),
        Email(),
        Unique(User.email)
    ]

    password_validators = [
        DataRequired(), 
        Length(8, 128)
    ]

    email = EmailField(validators=email_validators)
    password = PasswordField('Password', validators=password_validators)
    accept_tos = BooleanField('',validators=[DataRequired()])

class LoginForm(FlaskForm):
    next = HiddenField()
    email = StringField('Email', [DataRequired(), Length(3, 254)])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])

class GeneratePasswordResetForm(FlaskForm):
    email = StringField('Email', [DataRequired(), Length(3, 254)])

class PasswordUpdateForm(FlaskForm):
    old_password = PasswordField('Old Password')
    password = PasswordField('New Password', [
        DataRequired(),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class PasswordResetForm(FlaskForm):
    reset_token = HiddenField()
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])