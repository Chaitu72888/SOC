import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'snsoc.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ABUSEIPDB_API_KEY = os.environ.get('ABUSEIPDB_API_KEY', '')
    MOCK_TI_MODE = os.environ.get('MOCK_TI_MODE', 'true').lower() == 'true'

    # Comma-separated list of origins allowed to call the API
    ALLOWED_ORIGINS = [
        o.strip() for o in os.environ.get('ALLOWED_ORIGINS', '').split(',') if o.strip()
    ]
