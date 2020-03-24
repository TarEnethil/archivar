from app.models import User

# generate choices for dungeon masters (=users)
def gen_dm_choices():
    choices = []

    users = User.query.all()

    for user in users:
        choices.append((user.id, user.username))

    return choices