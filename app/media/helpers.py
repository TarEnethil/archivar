from app import app, db
from app.helpers import flash_no_permission
from app.models import Role, User, MediaItem, MediaCategory
from app.calendar.helpers import gen_calendar_stats
from flask_login import current_user
from sqlalchemy import and_, or_, not_
from werkzeug import secure_filename
import os

# check that user has the media admin role
def redirect_non_media_admins():
    if not current_user.is_media_admin():
        flash_no_permission()
        return True
    return False

# generate choices for the media category SelectField
def gen_media_category_choices():
    choices = []

    categories = MediaCategory.query.all()

    for cat in categories:
        choices.append((cat.id, cat.name))

    return choices

# get best available file name for an uploaded media item
def media_filename(initial_filename):
    filename = secure_filename(initial_filename)

    counter = 1
    while os.path.isfile(os.path.join(app.config["MEDIA_DIR"], filename)):
        split = filename.rsplit(".", 1)

        # fancy duplication avoidance (tm)
        filename = split[0] + "-" + str(counter) + "." + split[1]
        counter += 1

    return filename

# get all media visible to the user, can be filtered by category
def get_media(filter_category=None):
    if current_user.has_admin_role():
        media = MediaItem.query
    elif current_user.has_media_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        media = MediaItem.query.filter(not_(and_(MediaItem.is_visible == False, MediaItem.created_by_id.in_(admin_ids))))
    else:
        media = MediaItem.query.filter(or_(MediaItem.is_visible == True, MediaItem.created_by_id == current_user.id))

    if filter_category:
        media = media.filter_by(category_id = filter_category)

    media = media.order_by(MediaItem.id.asc()).all()

    return media