from app import db
from app.calendar.helpers import gen_calendar_stats
from app.event.models import Event, EventCategory
from app.user.models import Role, User
from flask import redirect, url_for, flash
from flask_login import current_user
from functools import wraps
from jinja2 import Markup
from sqlalchemy import and_, or_, not_

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