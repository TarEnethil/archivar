from jinja2 import Markup


def gen_session_choices(char):
    choices_dict = {}

    for sess in sorted(char.sessions, key=lambda x: x.date):
        campaign = sess.campaign.name
        if campaign not in choices_dict.keys():
            choices_dict[campaign] = []

        choices_dict[campaign].append((sess.id, sess.view_text()))

    choices = [(0, "None")]

    for campaign in choices_dict.keys():
        choices.append((Markup(campaign), choices_dict[campaign]))

    return choices
