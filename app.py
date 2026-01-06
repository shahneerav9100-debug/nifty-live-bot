import os, threading, requests, time
from flask import Flask

# --- PASTE YOUR NEW DETAILS HERE ---
TOKEN = "8119396994:AAFdhHdq8mRwaFyGsfxnzn5vMTFo43Nnl_Q"
CHAT_ID = "8033862332"

app = Flask(__name__)

def send_telegram(msg):
    # This automatically cleans the token and adds 'bot' prefix
    t = str(TOKEN).strip()
    if not t.startswith("bot"):
        t = f"bot{t}"
    
    url = f"https://api.telegram.org/{t}/sendMessage"
    payload = {"chat_id": str(CHAT_ID).strip(), "text": msg, "parse_mode": "Markdown"}
    
    try:
        r = requests.post(url, json=payload, timeout=15)
        print(f"TELEGRAM LOG: {r.status_code} - {r.text}", flush=True)
    except Exception as e:
        print(f"CONNECTION ERROR: {e}", flush=True)

@app.route('/')
def home():
    return "<h1>New Bot is Online</h1><p>Visit /test to verify connection.</p>"

@app.route('/test')
def test():
    send_telegram("🚀 *SUCCESS!* The new bot is connected and working!")
    return "Check your Telegram phone app now!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
