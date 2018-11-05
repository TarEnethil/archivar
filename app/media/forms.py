from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import Length, InputRequired, ValidationError

class SettingsForm(FlaskForm):
    default_visible = BooleanField("Events are visible by default")

    submit = SubmitField("Submit")

class MediaItemCreateForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(),Length(min=0, max=100)])
    category = SelectField("Category", coerce=int)
    file = FileField("File", validators=[FileRequired()])
    is_visible = BooleanField("Is publicly visible")

    def validate_file(self, file):
        if not "." in file.data.filename:
            raise ValidationError("No file extension found.")

    submit = SubmitField("Submit")

class MediaItemEditForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(),Length(min=0, max=100)])
    category = SelectField("Category", coerce=int)
    file = FileField("File")
    is_visible = BooleanField("Is publicly visible")

    def validate_file(self, file):
        if file.data and not "." in file.data.filename:
            raise ValidationError("No file extension found.")

    submit = SubmitField("Submit")

class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(),Length(min=0, max=100)])
    submit = SubmitField("Submit")