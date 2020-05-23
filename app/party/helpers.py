from app.character.models import Character

# generate choices for party member SelectField (multi-select)
def gen_party_members_choices(ensure=None):
    choices = []

    characters = Character.query.all()

    for char in characters:
        if char.is_visible or (ensure != None and char in ensure):
            choices.append((char.id, "{} ({})".format(char.name, char.player.username)))

    return choices