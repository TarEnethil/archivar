from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms_components import SelectMultipleField, ColorField
from wtforms.validators import Length, InputRequired

class CampaignCreateForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(),Length(min=0, max=100)])
    dm = SelectField("Dungeon Master / Game Master", validators=[InputRequired()],coerce=int)
    color = ColorField("Color")
    description = TextAreaField("Description", render_kw={"rows": 15})
    default_participants = SelectMultipleField("Default participants for sessions",coerce=int)

    submit = SubmitField("Create Campaign")

class CampaignEditForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(),Length(min=0, max=100)])
    dm = SelectField("Dungeon Master / Game Master", validators=[InputRequired()],coerce=int)
    color = ColorField("Color")
    description = TextAreaField("Description", render_kw={"rows": 15})
    dm_notes = TextAreaField("DM notes", render_kw={"rows": 15})
    default_participants = SelectMultipleField("Default participants for sessions",coerce=int)

    submit = SubmitField("Create Campaign")