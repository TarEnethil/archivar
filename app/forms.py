from app import db
from app.models import User, Role
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Member me?")
    submit = SubmitField("Sign in ")

class CreateUserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Password again", validators=[EqualTo("password")])

    # choices are populated later
    roles = SelectMultipleField("Roles")
    submit = SubmitField("Submit")

class EditProfileForm(FlaskForm):
    about = TextAreaField("About", validators=[Length(min=0, max=1000)])
    password = PasswordField("Password")
    password2 = PasswordField("Password again", validators=[EqualTo("password")])

    submit = SubmitField("Submit")

class EditProfileFormAdmin(FlaskForm):
    about = TextAreaField("About", validators=[Length(min=0, max=1000)])
    password = PasswordField("Password")
    password2 = PasswordField("Password again", validators=[EqualTo("password")])

    # choices are populated later
    roles = SelectMultipleField("Roles")

    submit = SubmitField("Submit")

class SettingsForm(FlaskForm):
    title = StringField("Title", validators=[Length(max=64)])
    submit = SubmitField("Submit")

class InstallForm(FlaskForm):
    admin_name = StringField("Admin username", validators=[DataRequired()])
    admin_password = PasswordField("Password", validators=[DataRequired(), EqualTo("admin_password2")])
    admin_password2 = PasswordField("Password again", validators=[DataRequired()])

    submit = SubmitField("Submit")

