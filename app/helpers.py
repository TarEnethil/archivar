from app import app
from flask import flash, redirect
from models import GeneralSetting, MapNodeType
from flask_login import current_user
from werkzeug import secure_filename
from wtforms.validators import ValidationError
import os

def redirect_non_admins():
    if not current_user.has_admin_role():
        flash("Operation not permitted.", "danger")
        redirect(url_for("index"))

def redirect_non_map_admins():
    if not current_user.is_map_admin():
        flash("Operation not permitted.", "danger")
        redirect(url_for("index"))

def page_title(dynamic_part=None):
    static_part = GeneralSetting.query.get(1).title

    if dynamic_part != None:
        return static_part + " - " + dynamic_part
    else:
        return static_part

def map_node_filename(filename_from_form):
    filename = secure_filename(filename_from_form)

    counter = 1
    while os.path.isfile(os.path.join(app.config["MAPNODES_DIR"], filename)):
        split = filename.rsplit(".", 1)

        # fancy duplication avoidance (tm)
        filename = split[0] + "-" + str(counter) + "." + split[1]
        counter += 1

    return filename

def gen_node_type_choices():
    choices = [(0, "choose...")]

    node_types = MapNodeType.query.all()

    for node_type in node_types:
        choices.append((node_type.id, node_type.name))

    return choices

class XYZ_Validator(object):
    def __call__(self, form, field):
        if not "{x}" in field.data or not "{y}" in field.data or not "{z}" in field.data:
            raise ValidationError("The tile provider needs the arguments {x} {y} and {z}")

class LessThanOrEqual(object):
    def __init__(self, comp_value_field_name):
        self.comp_value_field_name = comp_value_field_name

    def __call__(self, form, field):
        other_field = form._fields.get(self.comp_value_field_name)

        if other_field is None:
            raise Exception('No field named %s in form' % self.comp_value_field_name)

        if other_field.data and field.data:
            if field.data > other_field.data:
                raise ValidationError("Value must be less than or equal to %s" % self.comp_value_field_name)

class GreaterThanOrEqual(object):
    def __init__(self, comp_value_field_name):
        self.comp_value_field_name = comp_value_field_name

    def __call__(self, form, field):
        other_field = form._fields.get(self.comp_value_field_name)

        if other_field is None:
            raise Exception('No field named %s in form' % self.comp_value_field_name)

        if other_field.data and field.data:
            if field.data < other_field.data:
                raise ValidationError("Value must be greater than or equal to %s" % self.comp_value_field_name)