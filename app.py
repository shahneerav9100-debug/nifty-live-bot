import os, threading, requests, time
from flask import Flask

# --- PASTE YOUR TOKEN BELOW ---
# Example: "712345678:AAH_ExampleToken"
TOKEN = "8598972684:AAFAjrhlbY9Uyz7cYMcxJM0kl1lMVkTT0kQ"
CHAT_ID = "8033862332"

app = Flask(__name__)

def send_telegram(msg):
    # 1. Clean the token (removes spaces/new lines)
    clean_token = str(TOKEN).strip()
    
    # 2. Build the URL (ensuring 'bot' prefix is there only once)
    if not clean_token.startswith("bot"):
        url_token = f"bot{clean_token}"
    else:
        url_token = clean_token
        
    final_url = f"https://api.telegram.org/{url_token}/sendMessage"
    
    payload = {
        "chat_id": str(CHAT_ID).strip(),
        "text": msg,
        "parse_mode": "Markdown"
    }
    
    try:
        r = requests.post(final_url, json=payload, timeout=10)
        # This will now print the REAL reason for success or failure
        print(f"TELEGRAM DEBUG: Status {r.status_code} | Response: {r.text}", flush=True)
    except Exception as e:
        print(f"NETWORK ERROR: {e}", flush=True)

@app.route('/')
def home():
    return "Server is Live. Visit /test to trigger message."

@app.route('/test')
def test():
    send_telegram("🚀 *SUCCESS!* Your bot is finally talking to you!")
    return "Check your Render logs and Telegram phone app now."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
