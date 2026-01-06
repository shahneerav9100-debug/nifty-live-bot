import requests
import time
import sys

TOKEN = "8598972684:AAFAjrhlbY9Uyz7cYMcxJM0kl1lMVkTT0kQ"
CHAT_ID = "8033862332"

def send_telegram(msg):
    print(f"DEBUG: Attempting to send: {msg}", flush=True)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        print(f"DEBUG: Telegram Response Code: {r.status_code}", flush=True)
        print(f"DEBUG: Telegram Server Said: {r.text}", flush=True)
    except Exception as e:
        print(f"DEBUG: Connection Error: {e}", flush=True)

def run_bot():
    print("--- BOT STARTED ---", flush=True)
    send_telegram("🚀 BOT DEPLOYED: I am now online and tracking.")
    
    while True:
        # We use a very short sleep for testing so you see logs moving
        print("DEBUG: Bot is alive... waiting 30s", flush=True)
        time.sleep(30)
