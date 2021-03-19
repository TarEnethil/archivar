from app.helpers import generate_thumbnail as gen_thumb
from app.helpers import unique_filename
from flask import current_app
from jinja2 import Markup

def gen_session_choices(char):
    choices_dict = {}

    for sess in sorted(char.sessions, key=lambda x: x.date):
        campaign = sess.campaign.name
        if not campaign in choices_dict.keys():
            choices_dict[campaign] = []

        choices_dict[campaign].append((sess.id, sess.view_text()))

    choices = [(0, "None")]

    for campaign in choices_dict.keys():
        choices.append((Markup(campaign), choices_dict[campaign]))

    return choices

# get best available file name for an uploaded media item
def picture_filename(initial_filename):
    return unique_filename(current_app.config["PROFILE_PICTURE_DIR"], initial_filename)

def generate_thumbnail(filename):
    return gen_thumb(current_app.config['PROFILE_PICTURE_DIR'], filename, 100, 100)