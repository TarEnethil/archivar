from app.user.models import Role

# generate choices for the role SelectField
def gen_role_choices():
    role_choices = []

    all_roles = Role.query.all()
    for role in all_roles:
        role_choices.append((str(role.id), role.name + " --- (" + role.description + ")"))

    return role_choices

# generate the choices for the date format SelectField
def gen_date_string_choices():
    choices = []

    choices.append(("Do MMMM YYYY, HH:mm", "Sane"))
    choices.append(("ddd, Do MMMM YYYY, HH:mm", "Sane with weekdays"))
    choices.append(("dddd, Do MMMM YYYY, HH:mm", "Sane with weekdays long"))
    choices.append(("YYYY-MM-DD HH:mm", "ISO-Style"))
    choices.append(("LLL", "LLL"))
    choices.append(("DD.MM.YYYY, HH:mm", "European with time"))
    choices.append(("DD.MM.YYYY", "European date only"))
    choices.append(("MM/DD/YYYY, hh:mm A", "American with time"))
    choices.append(("MM/DD/YYYY", "American date only"))

    return choices