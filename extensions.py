import os
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

_allowed_origins = [o.strip() for o in os.environ.get('ALLOWED_ORIGINS', '').split(',') if o.strip()]

# Single shared SocketIO/Limiter instance for the whole app. Import these
# from here everywhere instead of creating a second SocketIO() in app.py.
socketio = SocketIO(cors_allowed_origins=_allowed_origins or [], async_mode='threading')
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
