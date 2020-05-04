"""generate thumbnails

Revision ID: b1d25db65c20
Revises: 44fb8dd89722
Create Date: 2020-05-01 13:21:03.178982

"""
from alembic import op
import sqlalchemy as sa

from app.media.models import MediaItem
from app.media.helpers import generate_thumbnail
from flask import current_app
from os import path

# revision identifiers, used by Alembic.
revision = 'b1d25db65c20'
down_revision = '44fb8dd89722'
branch_labels = None
depends_on = None


def upgrade():
    print("generating thumbnails for existing images")

    files = MediaItem.query.all()

    correct = 0
    exceptions = 0
    skipped_no_image = 0
    skipped_no_file = 0

    for f in files:

        if f.is_image():
            filepath = path.join(current_app.config["MEDIA_DIR"], f.filename)
            if path.isfile(filepath):
                try:
                    generate_thumbnail(f.filename)
                except Exception as err:
                    exceptions += 1
                    print("could not generate thumbnail for {}: {}".format(f.filename, err))
                else:
                    correct += 1
                    print("generated thumbnail for {}".format(f.filename))

            else:
                skipped_no_file += 1
                print("skipping {} as the file does not exist".format(f.filename))
        else:
            skipped_no_image += 1
            print("skipping {} as it is not an image".format(f.filename))

    print("proceseed {} files".format(len(files)))
    print("skipped {} as they weren't images".format(skipped_no_image))
    print("skipped {} because the file did not exist".format(skipped_no_file))
    print("error occured on {} images".format(exceptions))
    print("generated {} thumbnails".format(correct))

def downgrade():
    pass
