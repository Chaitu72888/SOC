"""
SNSOC Threat Intelligence Lookup Engine
"""
import os
import requests
from config import Config

def check_ip(ip_address):
    """
    Queries AbuseIPDB API or uses mock threat intelligence calculation.
    """
    mock_mode = os.environ.get('MOCK_TI_MODE', 'true').lower() == 'true' or getattr(Config, 'MOCK_TI_MODE', True)
    api_key = os.environ.get('ABUSEIPDB_API_KEY', '') or getattr(Config, 'ABUSEIPDB_API_KEY', '')

    # Check for private or loopback ranges
    if ip_address.startswith(('127.', '10.', '192.168.', '172.16.', '169.254.')):
        return {
            "ip": ip_address,
            "score": 0,
            "status": "Clean",
            "is_whitelisted": True,
            "total_reports": 0,
            "country": "Local Network"
        }

    if not mock_mode and api_key:
        try:
            url = 'https://api.abuseipdb.com/api/v2/check'
            headers = {'Accept': 'application/json', 'Key': api_key}
            params = {'ipAddress': ip_address, 'maxAgeInDays': '90'}
            resp = requests.get(url, headers=headers, params=params, timeout=5)
            if resp.status_code == 200:
                data = resp.json().get('data', {})
                score = data.get('abuseConfidenceScore', 0)
                return {
                    "ip": ip_address,
                    "score": score,
                    "status": "Malicious" if score > 70 else "Suspicious" if score > 30 else "Clean",
                    "total_reports": data.get('totalReports', 0),
                    "country": data.get('countryCode', 'Unknown')
                }
        except Exception:
            pass

    # Deterministic mock calculation for fallback/testing
    hash_val = sum(ord(c) for c in ip_address)
    mock_score = (hash_val * 17) % 100
    if ip_address in ['185.15.1.100', '45.33.32.156']:
        mock_score = 88

    return {
        "ip": ip_address,
        "score": mock_score,
        "status": "Malicious" if mock_score > 70 else "Suspicious" if mock_score > 30 else "Clean",
        "total_reports": mock_score // 5,
        "country": "US"
    }
