"""
Log Entry
"""

from application import db


levels = [
 ('info', "Info"),
 ('error', "Error"),
 ('debug', "Debug")
]

class DetailEntry(db.EmbeddedDocument):
    """
    Detail Log Entry
    """
    level = db.StringField(choices=levels)
    message = db.StringField()

class LogEntry(db.Document): #pylint: disable=too-few-public-methods
    """Log Entry"""

    datetime = db.DateTimeField()
    message = db.StringField()
    has_error = db.BooleanField(default=False)
    source = db.StringField()
    details = db.ListField(db.EmbeddedDocumentField(DetailEntry))
    traceback = db.StringField()


    meta = {"strict" : False,
            "indexes": [
                {'fields': ['datetime'],
                 'expireAfterSeconds': 2592000
                }
            ]
           }
