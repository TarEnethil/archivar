from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.validators import Length, InputRequired

class PartyForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(),Length(min=0, max=100)])
    profile_picture = FileField("Logo")
    description = TextAreaField("Description", render_kw={"rows": 15})
    members = SelectMultipleField("Members",coerce=int)

    submit = SubmitField("Submit")