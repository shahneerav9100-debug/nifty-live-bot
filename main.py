import os
import threading
import requests
import time
from flask import Flask

# --- YOUR CONFIG ---
TOKEN = "YOUR_TOKEN_HERE"
CHAT_ID = "YOUR_ID_HERE"

app = Flask(__name__)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": msg})
        print(f"Telegram Status: {r.status_code}", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

# This runs the bot logic
def run_bot():
    print("Bot background thread started!", flush=True)
    while True:
        # Every 5 minutes, it will just log to show it is alive
        print("Bot is ticking...", flush=True)
        time.sleep(300)

# Start the thread IMMEDIATELY when the file is loaded
threading.Thread(target=run_bot, daemon=True).start()

@app.route('/')
def home():
    send_telegram("🚀 Server just started up!")
    return "Bot is Active"

@app.route('/test')
def test():
    send_telegram("🔔 Test link clicked!")
    return "Success"
