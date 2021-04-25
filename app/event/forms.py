from app.validators import YearPerEpochValidator, DayPerMonthValidator
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, BooleanField, SelectField, widgets
from wtforms_components import ColorField
from wtforms.validators import Length, InputRequired


class SettingsForm(FlaskForm):
    default_category = SelectField("Default category", coerce=int)
    default_epoch = SelectField("Default epoch", coerce=int)
    default_year = IntegerField("Default year")

    submit = SubmitField("Save Settings")


class EventForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(min=0, max=100)])
    category = SelectField("Category", coerce=int)
    description = TextAreaField("Description", render_kw={"rows": 15})
    epoch = SelectField("Epoch", coerce=int, validators=[InputRequired()])
    year = IntegerField("Year", widget=widgets.Input(input_type="number"), validators=[InputRequired(),
                        YearPerEpochValidator("epoch")])
    month = SelectField("Month", coerce=int, validators=[InputRequired()])
    day = SelectField("Day", coerce=int, validators=[InputRequired(), DayPerMonthValidator("month")])
    duration = IntegerField("Duration (days)", default=1, validators=[InputRequired()])

    is_visible = BooleanField("Is publicly visible")

    submit = SubmitField("Submit")


class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(min=0, max=100)])
    color = ColorField("Color")

    submit = SubmitField("Submit")
