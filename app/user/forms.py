from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectMultipleField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError

class CreateUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    password2 = PasswordField("Password again", validators=[EqualTo("password")])

    # choices are populated later
    roles = SelectMultipleField("Roles")
    submit = SubmitField("Submit")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user is not None:
            raise ValidationError("Username already in use.")

class EditProfileForm(FlaskForm):
    about = TextAreaField("About", validators=[Length(min=0, max=1000)], render_kw={"rows": 15})
    password = PasswordField("Password")
    password2 = PasswordField("Password again", validators=[EqualTo("password")])

    # choices are populated later
    roles = SelectMultipleField("Roles")

    submit = SubmitField("Submit")