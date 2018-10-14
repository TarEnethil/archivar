from app.models import Character, Party, Session
from sqlalchemy import and_

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

def get_session_number(code):
    q = Session.query.filter(Session.code == code)
    return q.count()

def get_previous_session_id(date, code):
    q = Session.query.filter(and_(Session.code == code, Session.date < date)).order_by(Session.date.desc()).first()

    if q:
        return q.id
    else:
        return

def get_next_session_id(date, code):
    q = Session.query.filter(and_(Session.code == code, Session.date > date)).order_by(Session.date.asc()).first()

    if q:
        return q.id
    else:
        return