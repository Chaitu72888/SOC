import os
import json
import secrets
import time
import warnings
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_required
from config import Config
from extensions import socketio, limiter
from models import db, Operator, IDSRule, APIDataLog, PlatformSync, DataUsageSetting
import bcrypt

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Use the single shared SocketIO/Limiter instances from extensions.py
# instead of creating a second, unrelated SocketIO instance here.
socketio.init_app(app)
limiter.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Operator.query.get(int(user_id))

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin and origin in app.config.get('ALLOWED_ORIGINS', []):
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Platform'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Vary'] = 'Origin'
    return response

def seed_db():
    if not Operator.query.first():
        admin_name = os.environ.get('ADMIN_USER')
        admin_pass = os.environ.get('ADMIN_PASS')
        if not admin_name or not admin_pass:
            # No admin configured in the environment: generate a one-time
            # random password instead of shipping a hardcoded credential.
            admin_name = admin_name or 'admin'
            admin_pass = secrets.token_urlsafe(12)
            warnings.warn(
                f"No ADMIN_USER/ADMIN_PASS set. Generated operator "
                f"'{admin_name}' with a one-time password: {admin_pass} "
                f"(this is only printed once — save it now).",
                RuntimeWarning,
            )
        hashed = bcrypt.hashpw(admin_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin = Operator(name=admin_name, passcode_hash=hashed)
        db.session.add(admin)
    
    if not IDSRule.query.filter_by(rule_type='protected_port').first():
        for port in [22, 23, 445, 3389]:
            db.session.add(IDSRule(rule_type='protected_port', value=str(port)))
    
    if not IDSRule.query.filter_by(rule_type='threshold').first():
        db.session.add(IDSRule(rule_type='threshold', value=json.dumps({"max_packets": 100, "window_seconds": 10})))

    if not DataUsageSetting.query.first():
        db.session.add(DataUsageSetting(low_data_mode=False, refresh_interval='30s', wifi_only_sync=True, alert_threshold_mb=50.0))

    if not PlatformSync.query.first():
        db.session.add(PlatformSync(platform='Android App', last_sync=time.time() - 120, last_transferred_bytes=25088, sync_status='In Sync'))
        db.session.add(PlatformSync(platform='Web Dashboard', last_sync=time.time() - 45, last_transferred_bytes=39520, sync_status='In Sync'))

    if not APIDataLog.query.first():
        now = time.time()
        seeds = [
            APIDataLog(timestamp=now - 600, endpoint='/api/intel/lookup', platform='Android App', bytes_sent=420, bytes_recv=1840, ip='185.15.1.100', zone='Zone 1 (Main Stadium)', status='Malicious', score=88),
            APIDataLog(timestamp=now - 1500, endpoint='/api/intel/lookup', platform='Web Dashboard', bytes_sent=310, bytes_recv=1120, ip='8.8.8.8', zone='Zone 2 (Concourse)', status='Clean', score=0),
            APIDataLog(timestamp=now - 3600, endpoint='/api/intel/lookup', platform='Android App', bytes_sent=510, bytes_recv=2150, ip='192.168.1.45', zone='Zone 3 (VIP Lounge)', status='Suspicious', score=45),
            APIDataLog(timestamp=now - 7200, endpoint='/api/intel/lookup', platform='Android App', bytes_sent=430, bytes_recv=1920, ip='45.33.32.156', zone='Zone 1 (Main Stadium)', status='Malicious', score=92),
            APIDataLog(timestamp=now - 14400, endpoint='/api/intel/lookup', platform='Web Dashboard', bytes_sent=340, bytes_recv=1280, ip='1.1.1.1', zone='Zone 2 (Concourse)', status='Clean', score=0)
        ]
        db.session.add_all(seeds)

    db.session.commit()

# Register Blueprints
from auth import auth_bp
from api.dashboard import dashboard_bp
from api.ids import ids_bp
from api.intel import intel_bp
from api.block import block_bp
from api.telemetry import telemetry_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/api')
app.register_blueprint(ids_bp, url_prefix='/api/ids')
app.register_blueprint(intel_bp, url_prefix='/api/intel')
app.register_blueprint(block_bp, url_prefix='/api')
app.register_blueprint(telemetry_bp, url_prefix='/api/telemetry')

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

with app.app_context():
    db.create_all()
    seed_db()

# Start background tasks
from engine.capture import start_capture_thread
from engine.scorer import start_stats_thread
start_capture_thread(app, socketio)
start_stats_thread(app, socketio)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
