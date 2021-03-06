from app.character.models import Character

# generate choices for party member SelectField (multi-select)
def gen_party_members_choices():
    choices = []

    characters = Character.query.all()

    for char in characters:
        choices.append((char.id, "{} ({})".format(char.name, char.player.username)))

    return choices