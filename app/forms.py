from app import db
from models import Role
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Member me?")
    submit = SubmitField("Sign in ")

class EditProfileForm(FlaskForm):
    about = TextAreaField("About", validators=[Length(min=0, max=1000)])
    password = PasswordField("Password", validators=[EqualTo("password2")])
    password2 = PasswordField("Password again", validators=[EqualTo("password")])

    role_choices = []

    all_roles = Role.query.all()
    for role in all_roles:
        role_choices.append((str(role.id), role.name))

    roles = SelectMultipleField("Roles", choices=role_choices)
    submit = SubmitField("Submit")


