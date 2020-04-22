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

    campaigns = Campaign.campaigns

    for campaign in campaigns:
        choices.append((campaign.id, campaign.name))

    return choices

def gen_campaign_choices_admin():
    choices = []

    campaigns = Campaign.query.all()

    for campaign in campaigns:
        choices.append((campaign.id, campaign.name))

    return choices