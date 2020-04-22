from app import db
from app.calendar.helpers import gen_calendar_stats
from app.event.models import Event, EventCategory
from app.user.models import Role, User
from flask import redirect, url_for, flash
from flask_login import current_user
from functools import wraps
from sqlalchemy import and_, or_, not_

def gen_session_choices(char):
    choices = [(0, "None")]

    for s in char.sessions:
        choices.append((s.id, s.title))

    return choices