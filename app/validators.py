from flask_login import current_user
from wtforms.validators import ValidationError


# validate that a form field contains {x}, {y} and {z}
class ContainsXYZ(object):
    def __call__(self, form, field):
        if "{x}" not in field.data or "{y}" not in field.data or "{z}" not in field.data:
            raise ValidationError("The tile provider needs the arguments {x} {y} and {z}")


# validate that a form field contains a value that is <= that of another field
class IsLessOrEqual(object):
    def __init__(self, comp_value_field_name):
        self.comp_value_field_name = comp_value_field_name

    def __call__(self, form, field):
        other_field = form._fields.get(self.comp_value_field_name)

        if other_field is None:
            raise Exception(f'No field named {self.comp_value_field_name} in form')

        if other_field.data and field.data:
            if field.data > other_field.data:
                raise ValidationError(f"Value must be less than or equal to {self.comp_value_field_name}")


# validate that a form field contains a value that is >= that of another field
class IsGreaterOrEqual(object):
    def __init__(self, comp_value_field_name):
        self.comp_value_field_name = comp_value_field_name

    def __call__(self, form, field):
        other_field = form._fields.get(self.comp_value_field_name)

        if other_field is None:
            raise Exception(f'No field named {self.comp_value_field_name} in form')

        if other_field.data and field.data:
            if field.data < other_field.data:
                raise ValidationError(f"Value must be greater than or equal to {self.comp_value_field_name}")


# validate that a form field contains a year that is valid for a given epoch
class IsValidYearForEpoch(object):
    def __init__(self, epoch_id_field_name):
        self.epoch_field = epoch_id_field_name

    def __call__(self, form, field):
        from app.calendar.models import Epoch

        epoch_id = form._fields.get(self.epoch_field).data

        ep = Epoch.query.filter_by(id=epoch_id).first()

        if ep is None:
            raise ValidationError("Unknown epoch.")

        if field.data < 1:
            raise ValidationError(f"Year {field.data} is invalid for this epoch.")

        if ep.years != 0 and field.data > ep.years:
            raise ValidationError(f"Year {field.data} is invalid for this epoch.")


# validate that a form field contains a valid day for a given month
class IsValidDayForMonth(object):
    def __init__(self, month_id_field_name):
        self.month_field = month_id_field_name

    def __call__(self, form, field):
        from app.calendar.models import Month
        month_id = form._fields.get(self.month_field).data

        mo = Month.query.filter_by(id=month_id).first()

        if mo is None:
            raise ValidationError("Unknown month.")

        if field.data < 1 or field.data > mo.days:
            raise ValidationError(f"Day {field.data} is invalid for this month.")


# validate that a user is a DM of the campaign he wants to create a session for
class IsDMForCampaign(object):
    def __call__(self, form, field):
        from app.campaign.models import Campaign
        campaign_id = field.data
        campaign = Campaign.query.filter_by(id=campaign_id).first()

        if campaign is None:
            raise ValidationError("Unknown campaign.")

        if not current_user.is_dm_of(campaign) and not current_user.is_admin():
            raise ValidationError("You are not the DM of the selected campaign.")


# validate that a random table of given ID exists
class IsValidRandomTable(object):
    def __call__(self, form, field):
        from app.random.models import RandomTable
        table_id = field.data
        table = RandomTable.query.filter_by(id=table_id).first()

        if table is None:
            raise ValidationError("Random Table does not exist.")


# validate that a string is parseable by the r20 dice library
class IsValidDiceString(object):
    def __call__(self, form, field):
        from app.random.helpers import is_valid_dice_string
        if is_valid_dice_string(field.data) is False:
            raise ValidationError(f"{field.data} is not a valid dice string")
