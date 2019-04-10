from app.models import User
from app.user.helpers import gen_date_string_choices
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectMultipleField, SelectField, BooleanField, IntegerField
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

class SettingsForm(FlaskForm):
    dateformat = SelectField("Date format", choices=gen_date_string_choices(), validators=[InputRequired()])
    editor_height = IntegerField("Height of markdown editor (px)", validators=[InputRequired()])
    phb_session = BooleanField("Session: Use PHB-Style on markdown")
    phb_wiki = BooleanField("Wiki: Use PHB-Style on markdown")
    phb_character = BooleanField("Character: Use PHB-Style on markdown")
    phb_party = BooleanField("Party: Use PHB-Style on markdown")
    phb_calendar = BooleanField("Calendar: Use PHB-Style on markdown")

    submit = SubmitField("Submit")

class PasswordOnlyForm(FlaskForm):
    password = PasswordField("Password", validators=[InputRequired()])
    password2 = PasswordField("Password again", validators=[EqualTo("password")])

    submit = SubmitField("Submit")