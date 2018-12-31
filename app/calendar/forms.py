from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, BooleanField
from wtforms.validators import Length, InputRequired, NumberRange

class EpochForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(),Length(min=0, max=100)])
    abbreviation = StringField("Abbreviation", validators=[Length(min=0, max=5)])
    years = IntegerField("Duration in years (0 if current epoch)", default=0)
    circa = BooleanField("Duration is approximate (display only)")
    description = TextAreaField("Description", render_kw={"rows": 15})

    submit = SubmitField("Submit")

class MonthForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(),Length(min=0, max=100)])
    abbreviation = StringField("Abbreviation", validators=[Length(min=0, max=5)])
    days = IntegerField("Duration in days", validators=[InputRequired(),NumberRange(min=1)])
    description = TextAreaField("Description", render_kw={"rows": 15})

    submit = SubmitField("Submit")

class DayForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(),Length(min=0, max=100)])
    abbreviation = StringField("Abbreviation", validators=[Length(min=0, max=5)])
    description = TextAreaField("Description", render_kw={"rows": 15})

    submit = SubmitField("Submit")

class MoonForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(),Length(min=0, max=100)])
    phase_length = IntegerField("Phase length (days)", validators=[InputRequired(),NumberRange(min=2)])
    phase_offset = IntegerField("Phase shift (offset)", validators=[InputRequired(),NumberRange(min=0)], default=0)
    description = TextAreaField("Description", render_kw={"rows": 15})

    submit = SubmitField("Submit")