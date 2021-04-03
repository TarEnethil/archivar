from app.character.models import Character
from app.party.models import Party


# generate choices for party member SelectField (multi-select)
def gen_party_members_choices(ensure=None):
    choices = []

    characters = Character.query.all()

    for char in characters:
        if char.is_visible or (ensure is not None and char in ensure):
            choices.append((char.id, "{} ({})".format(char.name, char.player.username)))

    return choices


def gen_party_choices():
    choices = []

    parties = Party.query.all()

    for party in parties:
        choices.append((party.id, party.name))

    return choices
