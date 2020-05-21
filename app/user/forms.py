from app.user.helpers import gen_date_string_choices
from app.user.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError

class CreateUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    password2 = PasswordField("Password again", validators=[EqualTo("password")])

    role = SelectField("Role", coerce=int)
    submit = SubmitField("Create User")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user is not None:
            raise ValidationError("Username already in use.")

class EditProfileForm(FlaskForm):
    about = TextAreaField("About", validators=[Length(min=0, max=1000)], render_kw={"rows": 15})
    password = PasswordField("Password")
    password2 = PasswordField("Password again", validators=[EqualTo("password")])

    role = SelectField("Role", coerce=int)

    submit = SubmitField("Save Changes")

class SettingsForm(FlaskForm):
    dateformat = SelectField("Date format", choices=gen_date_string_choices(), validators=[InputRequired()])
    editor_height = IntegerField("Height of markdown editor (px)", validators=[InputRequired()])
    use_direct_links = BooleanField("Media sidebar: Use direct links")
    use_embedded_images = BooleanField("Media sidebar: Embed images")
    markdown_phb_style = BooleanField("Use PHB-Style for markdown")
    quicklinks = TextAreaField("Quicklinks", render_kw={"rows": 7})

    submit = SubmitField("Save settings")

class PasswordOnlyForm(FlaskForm):
    password = PasswordField("Password", validators=[InputRequired()])
    password2 = PasswordField("Password again", validators=[EqualTo("password")])

    submit = SubmitField("Change Password")