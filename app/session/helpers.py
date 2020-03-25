from app.models import Character, Party, Session
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
            p[1].append((member.id, member.name))

        choices.append(p)

    no_party_chars = Character.query.filter(Character.parties==None).all()

    if len(no_party_chars) > 0:
        p = ("No party", [])

        for char in no_party_chars:
            p[1].append((char.id, char.name))

        choices.append(p)

    return choices

# get the amount of sessions for the specified campaign code
def get_session_number(code):
    q = Session.query.filter(Session.code == code)
    return q.count()

# get the id of the previous session for a specified campaign code (if applicable)
def get_previous_session_id(session):
    q = Session.query.filter(and_(Session.campaign_id == session.campaign_id, Session.date < session.date)).order_by(Session.date.desc()).first()

    if q:
        return q.id
    else:
        return None

# get the id of the next session for a specified campaign code (if applicable)
def get_next_session_id(session):
    q = Session.query.filter(and_(Session.campaign_id == session.campaign_id, Session.date > session.date)).order_by(Session.date.asc()).first()

    if q:
        return q.id
    else:
        return None

# generate a list of used campaign codes (excluding '')
def gen_codes():
    q = Session.query.with_entities(Session.code).distinct().all()
    codes = []

    for tup in q:
        if tup[0] != '':
            codes.append(tup[0])

    return codes