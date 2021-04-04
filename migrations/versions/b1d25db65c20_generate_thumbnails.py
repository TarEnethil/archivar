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

    files = MediaItem.query.with_entities(MediaItem.filename).all()

    correct = 0
    exceptions = 0
    skipped_no_image = 0
    skipped_no_file = 0

    for f in files:
        if (f.split(".")[-1]).lower() in current_app.config["MAPNODES_FILE_EXT"]:
            filepath = path.join(current_app.config["MEDIA_DIR"], f.filename)
            if path.isfile(filepath):
                try:
                    generate_thumbnail(f.filename)
                except Exception as err:
                    exceptions += 1
                    print(f"could not generate thumbnail for {f.filename}: {err}")
                else:
                    correct += 1
                    print(f"generated thumbnail for {f.filename}")

            else:
                skipped_no_file += 1
                print(f"skipping {f.filename} as the file does not exist")
        else:
            skipped_no_image += 1
            print(f"skipping {f.filename} as it is not an image")

    if len(files) > 0:
        print(f"proceseed {len(files)} files")
        print(f"skipped {skipped_no_image} as they weren't images")
        print(f"skipped {skipped_no_file} because the file did not exist")
        print(f"error occured on {exceptions} images")
        print(f"generated {correct} thumbnails")


def downgrade():
    pass
