from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.validators import Length, InputRequired

class CreateCharacterForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=0, max=100),InputRequired()])
    race = StringField("Race", validators=[InputRequired()])
    class_ = StringField("Class", validators=[InputRequired()])
    description = TextAreaField("Description", render_kw={"rows": 15})

    submit = SubmitField("Submit")

class EditCharacterForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=0, max=100),InputRequired()])
    race = StringField("Race", validators=[InputRequired()])
    class_ = StringField("Class", validators=[InputRequired()])
    description = TextAreaField("Description", render_kw={"rows": 15})
    dm_notes = TextAreaField("DM Notes (hidden)", render_kw={"rows": 15})

    submit = SubmitField("Submit")

class PartyForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(),Length(min=0, max=100)])
    description = TextAreaField("Description", render_kw={"rows": 15})
    members = SelectMultipleField("Members",coerce=int)

    submit = SubmitField("Submit")