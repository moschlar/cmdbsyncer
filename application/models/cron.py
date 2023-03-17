"""
Cron Jobs
"""
from application import db, cron_register

intervals = [
    ("10min", "Every 10 minute"),
    ("hour", "Every hour"),
    ("daily", "Once Daily"),
]

class CronGroup(db.Document):
    """
    Cron Croup
    """

    name = db.StringField(required=True, unique=True)

    interval = db.StringField(choices=intervals)
    jobs = db.ListField(db.ReferenceField("CronJob"))

    enabled = db.BooleanField()

    meta = {
        'strict': False,
    }


commands = [
    ('cmk-export_hosts', "Checkmk: Export Hosts"),
    ('cmk-export_groups', "Checkmk: Export Groups"),
    ('cmk-export_rules', "Checkmk: Export Rules"),
    ('ansible-manage_hosts', "Ansible: Manage Hosts"),
    ('ansible-manage_servers', "Ansible: Manage Servers"),
]

class CronJob(db.Document):
    """
    Cron Job
    """
    name = db.StringField(required=True, unique=True)
    command = db.StringField(choices=cron_register.keys())
    account = db.ReferenceField('Account')
    params = db.ListField(db.StringField())

    def __str__(self):
        return f"{self.name} ({self.command})"



class CronStats(db.Document):
    """
    Cron Stats
    """

    group = db.StringField()
    last_run = db.DateTimeField()
    next_run = db.DateTimeField()
    last_message = db.StringField()