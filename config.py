import os
import warnings
from dotenv import load_dotenv

load_dotenv()

_DEFAULT_SECRET_KEY = 'default-soc-secret-key'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', _DEFAULT_SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'snsoc.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ABUSEIPDB_API_KEY = os.environ.get('ABUSEIPDB_API_KEY', '')
    MOCK_TI_MODE = os.environ.get('MOCK_TI_MODE', 'true').lower() == 'true'

    # Comma-separated list of origins allowed to call the API, e.g.
    # "https://your-dashboard.example.com,https://your-mobile-app.example.com"
    # Defaults to no cross-origin access at all until explicitly configured.
    ALLOWED_ORIGINS = [
        o.strip() for o in os.environ.get('ALLOWED_ORIGINS', '').split(',') if o.strip()
    ]

if Config.SECRET_KEY == _DEFAULT_SECRET_KEY:
    warnings.warn(
        "SECRET_KEY is not set (using the insecure built-in default). "
        "Set a real SECRET_KEY in your environment before deploying.",
        RuntimeWarning,
    )
