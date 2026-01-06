import requests
import time

TOKEN = "8598972684:AAFAjrhlbY9Uyz7cYMcxJM0kl1lMVkTT0kQ"
CHAT_ID = "8033862332"

def run_bot():
    print("Bot is starting up...", flush=True)
    while True:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": "🔔 TEST: If you see this, the connection is FIXED!"}
        
        try:
            response = requests.post(url, json=data)
            print(f"Sent message. Response: {response.status_code}", flush=True)
        except Exception as e:
            print(f"Error: {e}", flush=True)
            
        time.sleep(30) # Wait 30 seconds and try again

if __name__ == "__main__":
    run_bot()

