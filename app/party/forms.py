from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, InputRequired

class PartyForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(),Length(min=0, max=100)])
    description = TextAreaField("Description", render_kw={"rows": 15})
    dm_notes = TextAreaField("DM Notes", render_kw={"rows": 15})
    members = SelectMultipleField("Members",coerce=int)

    submit = SubmitField("Submit")