from app import app, db
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

def icon_is_valid(filename):
    if not "." in filename:
        raise ValidationError("No file extension found.")

    if not filename.rsplit(".", 1)[1].lower() in app.config["MAPNODES_FILE_EXT"]:
        raise ValidationError("Invalid file extension. File must be one of the following types: " + str(app.config["MAPNODES_FILE_EXT"]))

class MapNodeTypeCreateForm(FlaskForm):
    name = StringField("node name", validators=[DataRequired(), Length(max=64)])
    description = StringField("node description", validators=[Length(max=256)])
    icon = FileField("icon (x by x pixels recommended)", validators=[FileRequired()])

    submit = SubmitField("submit")

    def validate_icon(self, icon):
        icon_is_valid(icon.data.filename)        

class MapNodeTypeEditForm(FlaskForm):
    name = StringField("node name", validators=[DataRequired(), Length(max=64)])
    description = StringField("node description", validators=[Length(max=256)])
    icon = FileField("icon (x by x pixels recommended)")

    submit = SubmitField("submit")

    def validate_icon(self, icon):
        if icon.data:
            icon_is_valid(icon.data.filename)