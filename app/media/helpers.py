from app.helpers import upload_file, generate_thumbnail
from app.media.models import MediaItem, MediaCategory
from flask import current_app
from os import stat, path


# generate choices for the media category SelectField
def gen_media_category_choices():
    choices = []

    categories = MediaCategory.query.all()

    for cat in categories:
        choices.append((cat.id, cat.name))

    return choices


def upload_media_file(filedata, filename=None):
    path_ = current_app.config["MEDIA_DIR"]
    success, filename = upload_file(filedata, path_, filename)

    if success is False:
        return False, filename, 0

    size = stat(path.join(path_, filename)).st_size

    return True, filename, size


def generate_media_thumbnail(filename):
    return generate_thumbnail(current_app.config["MEDIA_DIR"], filename, 200, 200)


# get all media visible to the user, can be filtered by category
def get_media(filter_category=None):
    media = MediaItem.get_query_for_visible_items(include_hidden_for_user=True)

    if filter_category:
        media = media.filter_by(category_id=filter_category)

    media = media.order_by(MediaItem.id.asc()).all()

    return media
