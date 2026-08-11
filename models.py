from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Operator(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    passcode_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    force_password_change = db.Column(db.Boolean, default=True)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float, nullable=False)
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(32), nullable=False)
    src_ip = db.Column(db.String(64), nullable=False)
    dst_ip = db.Column(db.String(64), nullable=True)
    dst_port = db.Column(db.Integer, nullable=True)
    protocol = db.Column(db.String(16), nullable=True)
    status = db.Column(db.String(32), default='new')
    rule_name = db.Column(db.String(64), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'title': self.title,
            'message': self.message,
            'severity': self.severity,
            'src_ip': self.src_ip,
            'dst_ip': self.dst_ip,
            'dst_port': self.dst_port,
            'protocol': self.protocol,
            'status': self.status,
            'rule_name': self.rule_name
        }

class BlockedIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64), unique=True, nullable=False)
    reason = db.Column(db.String(256), nullable=True)
    blocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    blocked_by = db.Column(db.String(64), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'reason': self.reason,
            'blocked_at': self.blocked_at.isoformat() if self.blocked_at else None,
            'blocked_by': self.blocked_by
        }

class IDSRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule_type = db.Column(db.String(64), nullable=False) # 'protected_port' or 'threshold'
    value = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class APIDataLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float, nullable=False)
    endpoint = db.Column(db.String(128), nullable=False)
    platform = db.Column(db.String(64), nullable=False)
    bytes_sent = db.Column(db.Integer, nullable=False, default=0)
    bytes_recv = db.Column(db.Integer, nullable=False, default=0)
    ip = db.Column(db.String(64), nullable=True)
    zone = db.Column(db.String(128), nullable=True)
    status = db.Column(db.String(32), nullable=True)
    score = db.Column(db.Integer, nullable=True)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'endpoint': self.endpoint,
            'platform': self.platform,
            'bytes_sent': self.bytes_sent,
            'bytes_recv': self.bytes_recv,
            'ip': self.ip,
            'zone': self.zone,
            'status': self.status,
            'score': self.score
        }

class PlatformSync(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(64), nullable=False)
    last_sync = db.Column(db.Float, nullable=False)
    last_transferred_bytes = db.Column(db.Integer, nullable=False, default=0)
    sync_status = db.Column(db.String(32), nullable=False, default='In Sync')

    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'last_sync': self.last_sync,
            'last_transferred_bytes': self.last_transferred_bytes,
            'sync_status': self.sync_status
        }

class DataUsageSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    low_data_mode = db.Column(db.Boolean, default=False)
    refresh_interval = db.Column(db.String(32), default='30s')
    wifi_only_sync = db.Column(db.Boolean, default=True)
    alert_threshold_mb = db.Column(db.Float, default=50.0)

    def to_dict(self):
        return {
            'id': self.id,
            'low_data_mode': self.low_data_mode,
            'refresh_interval': self.refresh_interval,
            'wifi_only_sync': self.wifi_only_sync,
            'alert_threshold_mb': self.alert_threshold_mb
        }

