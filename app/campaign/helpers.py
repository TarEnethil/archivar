from app.helpers import generate_thumbnail as gen_thumb
from app.helpers import unique_filename
from flask import current_app
from flask_login import current_user
from app.campaign.models import Campaign
from app.user.models import User

# generate choices for dungeon masters (=users)
def gen_dm_choices():
    choices = []

    users = User.query.all()

    for user in users:
        choices.append((user.id, user.username))

    return choices

# generate choices for campaigns (for session form)
def gen_campaign_choices_dm():
    choices = []

    campaigns = current_user.campaigns

    for campaign in campaigns:
        choices.append((campaign.id, campaign.name))

    return choices

def gen_campaign_choices_admin():
    choices = []

    campaigns = Campaign.query.all()

    for campaign in campaigns:
        choices.append((campaign.id, campaign.name))

    return choices

# get best available file name for an uploaded media item
def picture_filename(initial_filename):
    return unique_filename(current_app.config["PROFILE_PICTURE_DIR"], initial_filename)

def generate_thumbnail(filename):
    return gen_thumb(current_app.config['PROFILE_PICTURE_DIR'], filename, 100, 100)