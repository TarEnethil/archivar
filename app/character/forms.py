from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectField
from wtforms.validators import Length, InputRequired

class CreateCharacterForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=0, max=100),InputRequired()])
    race = StringField("Race", validators=[InputRequired()])
    class_ = StringField("Class", validators=[InputRequired()])
    description = TextAreaField("Description", render_kw={"rows": 15})
    private_notes = TextAreaField("Private Notes (hidden)", render_kw={"rows": 15})

    submit = SubmitField("Submit")

class EditCharacterForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=0, max=100),InputRequired()])
    race = StringField("Race", validators=[InputRequired()])
    class_ = StringField("Class", validators=[InputRequired()])
    description = TextAreaField("Description", render_kw={"rows": 15})
    private_notes = TextAreaField("Private Notes (hidden)", render_kw={"rows": 15})
    dm_notes = TextAreaField("DM Notes (hidden)", render_kw={"rows": 15})

    submit = SubmitField("Submit")

class JournalForm(FlaskForm):
    title = StringField("Name", validators=[Length(min=0, max=100),InputRequired()])
    is_visible = BooleanField("Is publicly visible")
    content = TextAreaField("Description", render_kw={"rows": 15})
    session = SelectField("Belongs to Session", coerce=int)

    submit = SubmitField("Submit")
