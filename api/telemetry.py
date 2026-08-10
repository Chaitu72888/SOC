from flask import Blueprint, jsonify, request
from flask_login import login_required
from models import db, DataUsageSetting, PlatformSync, APIDataLog
import time

telemetry_bp = Blueprint('telemetry', __name__)

@telemetry_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def data_usage_settings():
    setting = DataUsageSetting.query.first()
    if not setting:
        setting = DataUsageSetting(low_data_mode=False, refresh_interval='30s', wifi_only_sync=True, alert_threshold_mb=50.0)
        db.session.add(setting)
        db.session.commit()

    if request.method == 'POST':
        data = request.json or {}
        if 'low_data_mode' in data:
            setting.low_data_mode = bool(data['low_data_mode'])
        if 'refresh_interval' in data:
            setting.refresh_interval = str(data['refresh_interval'])
        if 'wifi_only_sync' in data:
            setting.wifi_only_sync = bool(data['wifi_only_sync'])
        if 'alert_threshold_mb' in data:
            setting.alert_threshold_mb = float(data['alert_threshold_mb'])
        db.session.commit()

    return jsonify({"success": True, "data": setting.to_dict()})

@telemetry_bp.route('/sync', methods=['GET'])
@login_required
def platform_sync_status():
    syncs = PlatformSync.query.all()
    return jsonify({"success": True, "data": [s.to_dict() for s in syncs]})

@telemetry_bp.route('/logs', methods=['GET'])
@login_required
def telemetry_logs():
    limit = request.args.get('limit', 50, type=int)
    logs = APIDataLog.query.order_by(APIDataLog.timestamp.desc()).limit(limit).all()
    return jsonify({"success": True, "data": [l.to_dict() for l in logs]})
