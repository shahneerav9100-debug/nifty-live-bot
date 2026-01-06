import os
import threading
import requests
import time
from flask import Flask

# --- PASTE YOUR ACTUAL DETAILS HERE ---
TOKEN = "8598972684:AAFAjrhlbY9Uyz7cYMcxJM0kl1lMVkTT0kQ"
CHAT_ID = "8033862332"

app = Flask(__name__)

def send_telegram(msg):
    # Strip any accidental spaces from your token
    clean_token = TOKEN.strip() 
    
    # Ensure the URL is perfectly built with the slash
    url = f"https://api.telegram.org/bot{clean_token}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID.strip() if isinstance(CHAT_ID, str) else CHAT_ID,
        "text": msg
    }
    
    try:
        r = requests.post(url, json=payload)
        print(f"Telegram Output: {r.status_code} - {r.text}", flush=True)
    except Exception as e:
        print(f"Connection Error: {e}", flush=True)

# This is the "Engine" that runs in the background
def run_bot_logic():
    print("Background Engine: STARTED", flush=True)
    while True:
        # We will put your Nifty logic back here later
        time.sleep(60)

# START THE ENGINE IMMEDIATELY
threading.Thread(target=run_bot_logic, daemon=True).start()

@app.route('/')
def home():
    return "<h1>Status: ONLINE</h1><p>The bot engine is running in the background.</p>"

@app.route('/test')
def test_route():
    print("User clicked the /test link!", flush=True)
    send_telegram("🔔 SUCCESS! The /test route is working and the bot can talk to you.")
    return "<h1>Message Sent!</h1><p>Check your Telegram now.</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

