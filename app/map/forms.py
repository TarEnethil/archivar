from app.helpers import LessThanOrEqual, GreaterThanOrEqual, XYZ_Validator
from flask import current_app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, HiddenField, BooleanField
from wtforms_components import SelectField as BetterSelectField
from wtforms.validators import Length, ValidationError, InputRequired, NumberRange, Optional

def icon_is_valid(filename):
    if not "." in filename:
        raise ValidationError("No file extension found.")

    if not filename.rsplit(".", 1)[1].lower() in current_app.config["MAPNODES_FILE_EXT"]:
        raise ValidationError("Invalid file extension. File must be one of the following types: " + str(current_app.config["MAPNODES_FILE_EXT"]))

class MapSettingsForm(FlaskForm):
    check_interval = IntegerField("Map change check interval (seconds, 0 = disabled)", validators=[InputRequired(), NumberRange(min=0)])
    icon_anchor = SelectField("Icon Anchor", choices=[(0, "bottom"), (1, "center")],coerce=int)
    default_visible = BooleanField("New locations are visible by default")
    default_map = SelectField("Default map",validators=[Optional()],coerce=int)

    submit = SubmitField("Save Settings")

class MapForm(FlaskForm):
    name = StringField("Map name", validators=[InputRequired(), Length(max=100)])
    is_visible = BooleanField("Map is visible")
    external_provider = BooleanField("Use external map provider")
    tiles_path = StringField("Provider pattern (internal: relative to data/map/, external: full url for an {x}{y}{z} map provider)", validators=[InputRequired(), XYZ_Validator()])
    min_zoom = IntegerField("Min Zoom Level", validators=[InputRequired(), NumberRange(min=0, max=20), LessThanOrEqual("max_zoom")])
    max_zoom = IntegerField("Max Zoom Level", validators=[InputRequired(), NumberRange(min=0, max=20), GreaterThanOrEqual("min_zoom")])
    default_zoom = IntegerField("Default Zoom Level", validators=[InputRequired(), NumberRange(min=0, max=20), LessThanOrEqual("max_zoom"), GreaterThanOrEqual("min_zoom")])
    no_wrap = BooleanField("Repeat map on x-axis?")

    submit = SubmitField("submit")

class MapNodeForm(FlaskForm):
    name = StringField("Location Name", validators=[Length(max=64),InputRequired()])
    description = TextAreaField("Description", validators=[Length(min=0, max=10000)], render_kw={"rows": 10})
    node_type = SelectField("Location Type", validators=[InputRequired(),NumberRange(min=1,message="Choose a valid location type")],coerce=int)
    wiki_entry = BetterSelectField("Wiki Article",validators=[Optional()],coerce=int)
    submap = SelectField("Sub Map",validators=[Optional()],coerce=int)

    is_visible = BooleanField("Is approved / visible (to anyone)")

    coord_x = HiddenField(validators=[InputRequired()])
    coord_y = HiddenField(validators=[InputRequired()])

    submit = SubmitField("submit")

class MapNodeTypeCreateForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(max=64)])
    description = StringField("Description", validators=[Length(max=256)])
    icon = FileField("Icon (x by x pixels recommended)", validators=[FileRequired()])

    submit = SubmitField("Create Location Type")

    def validate_icon(self, icon):
        icon_is_valid(icon.data.filename)

class MapNodeTypeEditForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(max=64)])
    description = StringField("Description", validators=[Length(max=256)])
    icon = FileField("Icon (x by x pixels recommended)")

    submit = SubmitField("Save Location Type")

    def validate_icon(self, icon):
        if icon.data:
            icon_is_valid(icon.data.filename)

