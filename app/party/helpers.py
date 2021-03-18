from app.character.models import Character
from app.helpers import generate_thumbnail as gen_thumb
from app.helpers import unique_filename
from flask import current_app

# generate choices for party member SelectField (multi-select)
def gen_party_members_choices(ensure=None):
    choices = []

    characters = Character.query.all()

    for char in characters:
        if char.is_visible or (ensure != None and char in ensure):
            choices.append((char.id, "{} ({})".format(char.name, char.player.username)))

    return choices

# get best available file name for an uploaded media item
def picture_filename(initial_filename):
    return unique_filename(current_app.config["PROFILE_PICTURE_DIR"], initial_filename)

def generate_thumbnail(filename):
    return gen_thumb(current_app.config['PROFILE_PICTURE_DIR'], filename, 100, 100)