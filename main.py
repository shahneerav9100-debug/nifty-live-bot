import requests
import time
import os

# --- PASTE YOUR SECRETS HERE ---
TOKEN = "8598972684:AAFAjrhlbY9Uyz7cYMcxJM0kl1lMVkTT0kQ"
CHAT_ID = "8033862332"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        response = requests.post(url, json=payload)
        # This will show in Render Logs so we can see what happened
        print(f"Telegram Status: {response.status_code} | Response: {response.text}", flush=True)
    except Exception as e:
        print(f"Failed to reach Telegram: {e}", flush=True)

def run_bot():
    print("🚀 BOT ENGINE STARTED", flush=True)
    
    # This message should hit your phone THE MOMENT Render deploys
    send_telegram("🔔 ALERT: Connection Successful! Your bot is now talking to your phone.")
    
    while True:
        print("Bot is looping and waiting...", flush=True)
        time.sleep(60)

if __name__ == "__main__":
    run_bot()
