from flask import flash
from app import db
from app.models import GeneralSetting, Epoch, Month
from flask_login import current_user
from sqlalchemy import func
from wtforms.validators import ValidationError

# flash generic error message
def flash_no_permission(msg=None):
    if (msg != None):
        flash(msg)
    else:
        flash("No permission for this action.", "danger")

# check that user has the admin role
def redirect_non_admins():
    if not current_user.has_admin_role():
        flash_no_permission()
        return True
    return False

# check that user has admin role or a character in the party
def redirect_non_admins_non_party(party):
    if not current_user.has_admin_role() and not current_user.has_char_in_party(party):
        flash_no_permission()
        return True

    return False

# check that user has admin role or a character in the session
def redirect_non_admins_non_session(session):
    if not current_user.has_admin_role() and not current_user.has_char_in_session(session):
        flash_no_permission()
        return True

    return False

# generate the page <title>
def page_title(dynamic_part=None):
    gset = GeneralSetting.query.get(1)

    if not gset:
        static_part = ""
    else:
        static_part = gset.title

    if dynamic_part != None:
        return static_part + " - " + dynamic_part
    else:
        return static_part

# stretch color code from #xxx to #xxxxxx if needed
def stretch_color(color):
    if len(color) == 4:
        return "#" + color[1] + color[1] + color[2] + color[2] + color[3] + color[3]
    return color

# make a COUNT(id) query for a db object
def count_rows(db_class):
    return db.session.query(func.count(db_class.id)).scalar()

# validate that a form field contains {x}, {y} and {z}
class XYZ_Validator(object):
    def __call__(self, form, field):
        if not "{x}" in field.data or not "{y}" in field.data or not "{z}" in field.data:
            raise ValidationError("The tile provider needs the arguments {x} {y} and {z}")

# validate that a form field contains a value that is <= that of another field
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

# validate that a form field contains a value that is >= that of another field
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

# validate that a form field contains a year that is valid for a given epoch
class YearPerEpochValidator(object):
    def __init__(self, epoch_id_field_name):
        self.epoch_field = epoch_id_field_name

    def __call__(self, form, field):
        epoch_id = form._fields.get(self.epoch_field).data

        ep = Epoch.query.filter_by(id=epoch_id).first()

        if ep == None:
            raise ValidationError("Unknown epoch.")

        if ep.years != 0 and (field.data < 1 or field.data > ep.years):
            raise ValidationError("Year " + field.data + " is invalid for this epoch.")

# validate that a form field contains a valid day for a given month
class DayPerMonthValidator(object):
    def __init__(self, month_id_field_name):
        self.month_field = month_id_field_name

    def __call__(self, form, field):
        month_id = form._fields.get(self.month_field).data

        mo = Month.query.filter_by(id=month_id).first()

        if mo == None:
            raise ValidationError("Unknown month.")

        if field.data < 1 or field.data > mo.days:
            raise ValidationError("Day " + field.data + " is invalid for this month.")