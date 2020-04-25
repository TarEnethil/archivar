from app import db
from app.character.models import Character
from app.party.models import Party
from app.session.models import Session
from sqlalchemy import and_

# generate choices for session participant SelectField (multi-select)
# tuples are nested by party (=optgroup)
def gen_participant_choices():
    choices = []

    parties = Party.query.all()

    for party in parties:
        if len(party.members) == 0:
            continue

        p = (party.name, [])

        for member in party.members:
            p[1].append((member.id, "%s (%s)" % (member.name, member.player.username)))

        choices.append(p)

    no_party_chars = Character.query.filter(Character.parties==None).all()

    if len(no_party_chars) > 0:
        p = ("No party", [])

        for char in no_party_chars:
            p[1].append((char.id, "%s (%s)" % (char.name, char.player.username)))

        choices.append(p)

    return choices

# get the previous session for a specified campaign code (if applicable)
def get_previous_session(session):
    q = Session.query.filter(and_(Session.campaign_id == session.campaign_id, Session.date < session.date)).order_by(Session.date.desc()).first()
    return q

# get the next session for a specified campaign (if applicable)
def get_next_session(session):
    q = Session.query.filter(and_(Session.campaign_id == session.campaign_id, Session.date > session.date)).order_by(Session.date.asc()).first()
    return q

def recalc_session_numbers(campaign, db):
    print("recalc called")
    sessions = Session.query.filter(Session.campaign_id == campaign.id).order_by(Session.date.asc()).all()
    count = 1

    for session in sessions:
        session.session_number = count
        count += 1

    db.session.commit()