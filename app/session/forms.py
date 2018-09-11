from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, DateTimeField
from wtforms_components import SelectMultipleField
from wtforms.validators import Length, InputRequired

class SessionForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(),Length(min=0, max=100)])
    code = StringField("Campaign code", validators=[Length(min=0,max=5)])
    add_session_no = BooleanField("Prepend session number to title")
    summary = TextAreaField("Summary", render_kw={"rows": 15})
    dm_notes = TextAreaField("DM Notes", render_kw={"rows": 15})
    date = DateTimeField("Date", validators=[InputRequired()], format="%Y-%m-%d %H:%M")
    participants = SelectMultipleField("Participants", coerce=int)

    submit = SubmitField("Submit")