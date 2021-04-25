from flask_wtf import FlaskForm
from app.validators import IsDMValidator
from wtforms import StringField, TextAreaField, SubmitField, DateTimeField, SelectField, HiddenField
from wtforms_components import SelectMultipleField
from wtforms.validators import Length, InputRequired


class SessionForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), Length(min=0, max=100)])
    campaign = HiddenField("Campaign", validators=[InputRequired(), IsDMValidator("campaign")])
    summary = TextAreaField("Summary", render_kw={"rows": 15})
    dm_notes = TextAreaField("DM Notes", render_kw={"rows": 15})
    date = DateTimeField("Date", validators=[InputRequired()], format="%Y-%m-%d %H:%M")
    participants = SelectMultipleField("Participants", coerce=int)

    submit = SubmitField("Submit")


class CampaignSelectForm(FlaskForm):
    campaigns = SelectField("Campaign", validators=[InputRequired(), IsDMValidator("campaigns")], coerce=int)

    submit = SubmitField("Create Session")
