"""
SOC Threat Analytics Scorer Module
"""
import threading
import time

def start_stats_thread(app, socketio):
    """
    Spawns background SOC threat analytics scoring thread.
    """
    def scorer_loop():
        with app.app_context():
            while True:
                time.sleep(15)

    thread = threading.Thread(target=scorer_loop, daemon=True)
    thread.start()
    return thread
