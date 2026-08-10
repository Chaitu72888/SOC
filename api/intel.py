import os
import json
import time
import ipaddress
from flask import Blueprint, jsonify, request
from flask_login import login_required
from models import db, APIDataLog
from config import Config
from engine.threat_intel import check_ip

intel_bp = Blueprint('intel', __name__)

@intel_bp.route('/config', methods=['POST'])
@login_required
def update_config():
    data = request.json or {}
    api_key = data.get('api_key', '')
    mock_mode = data.get('mock_mode', True)
    
    os.environ['ABUSEIPDB_API_KEY'] = api_key
    os.environ['MOCK_TI_MODE'] = 'true' if mock_mode else 'false'
    
    Config.ABUSEIPDB_API_KEY = api_key
    Config.MOCK_TI_MODE = mock_mode
    
    return jsonify({"success": True, "data": {"mode": "mock" if mock_mode else "live"}})

@intel_bp.route('/lookup', methods=['POST'])
@login_required
def lookup_ip():
    req_data = request.json or {}
    ip = req_data.get('ip')
    if not ip:
        return jsonify({"success": False, "error": "ip required"}), 400
        
    zone = req_data.get('zone', 'Zone 1 (Main Stadium)')
    platform = request.headers.get('X-Platform') or req_data.get('platform', 'Web Dashboard')

    # Calculate request bytes
    request_raw = json.dumps(req_data)
    bytes_sent = len(request_raw.encode('utf-8')) + 150

    res = check_ip(ip)
    score = res.get('score', 0)
    status = 'Malicious' if score > 70 else 'Suspicious' if score > 30 else 'Clean'

    response_body = {
        "success": True,
        "data": res
    }
    
    # Calculate response bytes
    response_raw = json.dumps(response_body)
    bytes_recv = len(response_raw.encode('utf-8')) + 200

    # Save data usage log in DB
    log_entry = APIDataLog(
        timestamp=time.time(),
        endpoint='/api/intel/lookup',
        platform=platform,
        bytes_sent=bytes_sent,
        bytes_recv=bytes_recv,
        ip=ip,
        zone=zone,
        status=status,
        score=score
    )
    db.session.add(log_entry)
    db.session.commit()

    return jsonify(response_body)
