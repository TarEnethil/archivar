from app import app
from app.helpers import flash_no_permission
from app.models import MapNodeType
from flask_login import current_user
from werkzeug import secure_filename
import os

def redirect_non_map_admins():
    if not current_user.is_map_admin():
        flash_no_permission()
        return True
    return False

def map_node_filename(filename_from_form):
    filename = secure_filename(filename_from_form)

    counter = 1
    while os.path.isfile(os.path.join(app.config["MAPNODES_DIR"], filename)):
        split = filename.rsplit(".", 1)

        # fancy duplication avoidance (tm)
        filename = split[0] + "-" + str(counter) + "." + split[1]
        counter += 1

    return filename

def gen_node_type_choices():
    choices = [(0, "choose...")]

    node_types = MapNodeType.query.all()

    for node_type in node_types:
        choices.append((node_type.id, node_type.name))

    return choices