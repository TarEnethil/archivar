from app import app, db
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from app.helpers import LessThanOrEqual, GreaterThanOrEqual
from wtforms import StringField, TextAreaField, SubmitField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, InputRequired, NumberRange

def icon_is_valid(filename):
    if not "." in filename:
        raise ValidationError("No file extension found.")

    if not filename.rsplit(".", 1)[1].lower() in app.config["MAPNODES_FILE_EXT"]:
        raise ValidationError("Invalid file extension. File must be one of the following types: " + str(app.config["MAPNODES_FILE_EXT"]))

class MapSettingsForm(FlaskForm):
    api_key = StringField("GoogleMaps API Key", validators=[InputRequired(), Length(max=64)])

    # TODO: validation
    min_zoom = IntegerField("Min Zoom Level", validators=[InputRequired(), NumberRange(min=0, max=20), LessThanOrEqual("max_zoom")])
    max_zoom = IntegerField("Max Zoom Level", validators=[InputRequired(), NumberRange(min=0, max=20), GreaterThanOrEqual("min_zoom")])
    default_zoom = IntegerField("Default Zoom Level", validators=[InputRequired(), NumberRange(min=0, max=20), LessThanOrEqual("max_zoom"), GreaterThanOrEqual("min_zoom")])

    tiles_path = StringField("directory/path for map tiles (relative to data/map)")

    submit = SubmitField("submit")

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

