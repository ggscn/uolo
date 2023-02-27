from collections import OrderedDict

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FormField,BooleanField, FileField, DateField, SelectField, FloatField, IntegerField,SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional
from flask_app.blueprints.user.models import RoleEnum


class UserForm(FlaskForm):
    email = StringField('email')
    role = SelectField('role', choices=RoleEnum.choices())


