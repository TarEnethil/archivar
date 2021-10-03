from app.validators import HasFileExtension
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import Length, InputRequired


class SettingsForm(FlaskForm):
    default_visible = BooleanField("Media items are visible by default")

    submit = SubmitField("Save settings")


class MediaItemCreateForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(min=0, max=100)])
    category = SelectField("Category", coerce=int)
    file = FileField("File", validators=[FileRequired(), HasFileExtension()])
    is_visible = BooleanField("Is publicly visible", default=True)

    submit = SubmitField("Upload File")


class MediaItemEditForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(min=0, max=100)])
    category = SelectField("Category", coerce=int)
    file = FileField("File", validators=[HasFileExtension(optional=True)])
    is_visible = BooleanField("Is publicly visible")

    submit = SubmitField("Save Item")


class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(min=0, max=100)])
    submit = SubmitField("Submit")
