"""
============================================================================
Locust Load Test Script: Baseline & Performance Load Testing
File: load-tests/locustfile.py
Description: Simulates 100 concurrent virtual users executing requests continuously 
             for 1 minute against the SNSOC backend API.
Target Metrics: RPS, Min/Max/Avg Response Times, p95/p99 Percentiles, Failures.
============================================================================
"""

from locust import HttpUser, task, between, events
import json
import random

class SNSOCBackendUser(HttpUser):
    # Think time between user requests (simulate realistic user behavior)
    wait_time = between(0.1, 0.5)

    def on_start(self):
        """Runs once per virtual user when spawned - performs login authentication."""
        self.client.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "LocustLoadTester/1.0"
        })
        # Login scenario
        response = self.client.post("/auth/login", data={
            "username": "admin",
            "password": "admin123"
        }, catch_response=True)
        if response.status_code in [200, 302]:
            response.success()
        else:
            response.failure(f"Login failed with status code: {response.status_code}")

    @task(4)
    def test_intel_lookup_endpoint(self):
        """High frequency endpoint: IP Threat Intelligence Lookup (/api/intel/lookup)."""
        sample_ips = ["185.15.1.100", "8.8.8.8", "192.168.1.45", "45.33.32.156", "1.1.1.1"]
        payload = {
            "ip": random.choice(sample_ips),
            "zone": "Zone 1 (Main Stadium)",
            "platform": "Locust Load Tester"
        }
        with self.client.post("/api/intel/lookup", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Intel lookup failed: {response.status_code}")

    @task(3)
    def test_telemetry_logs_endpoint(self):
        """High frequency endpoint: Telemetry Logs Retrieval (/api/telemetry/logs)."""
        with self.client.get("/api/telemetry/logs?limit=50", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Telemetry logs failed: {response.status_code}")

    @task(2)
    def test_platform_sync_endpoint(self):
        """Medium frequency endpoint: Platform Sync Status (/api/telemetry/sync)."""
        with self.client.get("/api/telemetry/sync", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Platform sync failed: {response.status_code}")

    @task(1)
    def test_telemetry_settings_endpoint(self):
        """Low frequency endpoint: Data Usage Settings (/api/telemetry/settings)."""
        with self.client.get("/api/telemetry/settings", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Settings retrieval failed: {response.status_code}")

    @task(1)
    def test_dashboard_home_render(self):
        """Page render endpoint: Dashboard Home Page (/)."""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code in [200, 302]:
                response.success()
            else:
                response.failure(f"Dashboard render failed: {response.status_code}")

# Command to execute Locust:
# locust -f load-tests/locustfile.py --host=http://127.0.0.1:5000 --users 100 --spawn-rate 20 --run-time 1m --headless --csv=load-tests/locust_summary
