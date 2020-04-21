from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign in")

class SettingsForm(FlaskForm):
    title = StringField("Title", validators=[Length(max=64)])
    world_name = StringField("Worldname", validators=[Length(max=64)])
    welcome_page = TextAreaField("Text for welcome page", render_kw={"rows": 20})
    quicklinks = TextAreaField("Quicklinks", render_kw={"rows": 7})
    submit = SubmitField("Save Settings")

class InstallForm(FlaskForm):
    admin_name = StringField("Admin username", validators=[DataRequired()])
    admin_password = PasswordField("Password", validators=[DataRequired(), EqualTo("admin_password2")])
    admin_password2 = PasswordField("Password again", validators=[DataRequired()])

    default_mapnodes = BooleanField("Install default lccation types (city, village,...)")

    submit = SubmitField("Install Archivar")

