from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "✅ XO Bot is alive! 🎮"

@app.route('/health')
def health():
    return {"status": "ok", "message": "Bot is running"}

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()