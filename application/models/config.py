"""
Config for the Syncer
"""
from application import db, app
class Config(db.Document):
    """
    Config Values
    """

    export_labels_list = db.ListField(db.StringField())
    export_inventory_list = db.ListField(db.StringField())
