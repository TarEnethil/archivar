from app import db
from app.helpers import urlfriendly
from app.user.models import LinkGenerator, SimpleAuditMixin
from datetime import datetime
from flask import url_for
from flask_misaka import markdown

class MapSetting(db.Model, SimpleAuditMixin):
    __tablename__ = "map_settings"
    id = db.Column(db.Integer, primary_key=True)
    icon_anchor = db.Column(db.Integer)
    default_visible = db.Column(db.Boolean, default=False)
    check_interval = db.Column(db.Integer, default=30)
    default_map = db.Column(db.Integer, db.ForeignKey("maps.id"), default=0)

class Map(db.Model, SimpleAuditMixin, LinkGenerator):
    __tablename__ = "maps"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    min_zoom = db.Column(db.Integer)
    max_zoom = db.Column(db.Integer)
    default_zoom = db.Column(db.Integer)
    tiles_path = db.Column(db.String(128), default="tile_{z}_{x}-{y}.png")
    external_provider = db.Column(db.Boolean, default=False)
    no_wrap = db.Column(db.Boolean, default=True)
    last_change = db.Column(db.DateTime, default=datetime.utcnow)
    is_visible = db.Column(db.Boolean, default=True)

    def to_dict(self):
        dic = {
            "id" : self.id,
            "name" : self.name,
        }

        return dic

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return self.name

    def view_url(self):
        return url_for('map.view', id=self.id, name=urlfriendly(self.name))

    def edit_url(self):
        return url_for('map.edit', id=self.id, name=urlfriendly(self.name))

    def settings_url(self):
        return url_for("map.map_settings", id=self.id, name=urlfriendly(self.name))

    def settings_button(self, ids=None):
        url = self.settings_url()
        return self.button(url=url, text="Settings", icon="cog", ids=None, classes="btn btn-default")

class MapNodeType(db.Model, SimpleAuditMixin):
    __tablename__ = "map_node_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(256))
    icon_file = db.Column(db.String(64))
    icon_width = db.Column(db.Integer)
    icon_height = db.Column(db.Integer)

    def to_dict(self):
        dic = {
            "id" : self.id,
            "name" : self.name,
            "description" : self.description,
            "icon_file" : url_for("map.node_type_icon", filename=self.icon_file),
            "icon_width": self.icon_width,
            "icon_height": self.icon_height
        }

        return dic

class MapNode(db.Model, SimpleAuditMixin):
    __tablename__ = "map_nodes"
    id = db.Column(db.Integer, primary_key=True)
    coord_x = db.Column(db.Float)
    coord_y = db.Column(db.Float)
    name = db.Column(db.String(64))
    description = db.Column(db.String(10000))
    node_type = db.Column(db.Integer, db.ForeignKey("map_node_types.id"))
    is_visible = db.Column(db.Boolean, default=False)
    wiki_entry_id = db.Column(db.Integer, db.ForeignKey("wiki_entries.id"), default=0)
    on_map = db.Column(db.Integer, db.ForeignKey("maps.id"))
    parent_map = db.relationship("Map", foreign_keys=[on_map])
    submap = db.Column(db.Integer, db.ForeignKey("maps.id"), default=0)

    def to_dict(self):
        dic = {
            "id" : self.id,
            "x" : self.coord_x,
            "y" : self.coord_y,
            "name" : self.name,
            "desc" : markdown(self.description, tables=True, fenced_code=True, escape=True),
            "node_type" : self.node_type,
            "visible" : self.is_visible,
            "created" : self.created,
            "created_by" : self.created_by.username,
            "wiki_id" : self.wiki_entry_id,
            "submap" : self.submap
        }

        if self.edited_by:
            # do update here because otherwise, this lands in a list of length one for some reason
            dic.update({
                "edited" : self.edited,
                "edited_by" : self.edited_by.username
            })

        return dic

    def sidebar_dict(self):
        dic = {
            "id" : self.id,
            "name" : self.name,
            "visible": self.is_visible
        }

        return dic