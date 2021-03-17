from app.helpers import generate_thumbnail as gen_thumb
from app.helpers import unique_filename
from app.media.models import MediaItem, MediaCategory
from flask import redirect, url_for, flash, current_app
from flask_login import current_user
from functools import wraps

# generate choices for the media category SelectField
def gen_media_category_choices():
    choices = []

    categories = MediaCategory.query.all()

    for cat in categories:
        choices.append((cat.id, cat.name))

    return choices

# get best available file name for an uploaded media item
def media_filename(initial_filename):
    return unique_filename(current_app.config["MEDIA_DIR"], initial_filename)

def generate_thumbnail(filename):
    return gen_thumb(current_app.config["MEDIA_DIR"], filename, 200, 200)

# get all media visible to the user, can be filtered by category
def get_media(filter_category=None):
    media = MediaItem.get_query_for_visible_items(include_hidden_for_user=True)

    if filter_category:
        media = media.filter_by(category_id = filter_category)

    media = media.order_by(MediaItem.id.asc()).all()

    return media
