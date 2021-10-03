from app.validators import IsValidRandomTable, IsValidDiceString
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, HiddenField
from wtforms.validators import Length, InputRequired, NumberRange


class DiceSetForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=0, max=100), InputRequired()])
    dice_string = StringField("Roll Expression",
                              validators=[Length(min=1, max=100), InputRequired(), IsValidDiceString()])

    submit = SubmitField("Submit")


class RandomTableForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=0, max=100), InputRequired()])
    description = TextAreaField("Description", render_kw={"rows": 15})

    submit = SubmitField("Submit")


class RandomTableEntryForm(FlaskForm):
    title = StringField("Name", validators=[Length(min=0, max=100), InputRequired()])
    weight = IntegerField("Weight", validators=[InputRequired(), NumberRange(min=1)], default=1)
    description = TextAreaField("Description", render_kw={"rows": 15})

    table = HiddenField("Table", validators=[InputRequired(), IsValidRandomTable()])

    submit = SubmitField("Submit")
