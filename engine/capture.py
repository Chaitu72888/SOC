"""
Network Telemetry Capture Module
"""
import threading
import time

def start_capture_thread(app, socketio):
    """
    Spawns background network telemetry monitoring thread.
    """
    def capture_loop():
        with app.app_context():
            while True:
                time.sleep(10)

    thread = threading.Thread(target=capture_loop, daemon=True)
    thread.start()
    return thread
