from app.models import Role

def gen_role_choices():
    role_choices = []

    all_roles = Role.query.all()
    for role in all_roles:
        role_choices.append((str(role.id), role.name + " --- (" + role.description + ")"))

    return role_choices

def gen_date_string_choices():
    choices = []

    choices.append(("Do MMMM YYYY, HH:mm", "Sane"))
    choices.append(("YYYY-MM-DD HH:mm", "ISO-Style"))
    choices.append(("LLL", "LLL"))
    choices.append(("DD.MM.YYYY, HH:mm", "European with time"))
    choices.append(("DD.MM.YYYY", "European date only"))
    choices.append(("MM/DD/YYYY, hh:mm A", "American with time"))
    choices.append(("MM/DD/YYYY", "American date only"))

    return choices