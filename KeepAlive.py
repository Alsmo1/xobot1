from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    # دي الرسالة اللي بيشوفها UptimeRobot لما بيزور الرابط
    return "Hello!is alive!"

def _run():
    # تشغيل السيرفر على الـ Host والـ Port اللي بيستخدمهم Replit
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8080))
    # use_reloader=False to avoid creating multiple threads/processes when imported
    app.run(host=host, port=port, threaded=True, debug=False, use_reloader=False)

def keep_alive():
    """
    Start the Flask keep-alive server in a daemon thread.

    Returns:
        threading.Thread: the thread running the Flask app (daemon=True)
    """
    t = Thread(target=_run, daemon=True)
    t.start()
    return t

# Optional: run the server when executing this module directly (useful for local testing)
if __name__ == "__main__":
    keep_alive()
