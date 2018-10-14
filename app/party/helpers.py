from app.models import Character

def gen_party_members_choices():
    choices = []

    characters = Character.query.all()

    for char in characters:
        choices.append((char.id, char.name + " ("+ char.player.username +")"))

    return choices