from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, BooleanField
from wtforms_components import ColorField
from wtforms.validators import Length, InputRequired

class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(),Length(min=0, max=100)])
    color = ColorField("Color")

    submit = SubmitField("Submit")