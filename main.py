import requests, time

TOKEN = "8598972684:AAFAjrhlbY9Uyz7cYMcxJM0kl1lMVkTT0kQ"
CHAT_ID = "8033862332"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

def run_bot():
    # This will run the second you click 'Deploy'
    print("DEBUG: Attempting to send message...")
    send_telegram("🚨 DEBUG TEST: The bot is alive on Render!")
    
    while True:
        print("DEBUG: I am awake and waiting...")
        time.sleep(60)

if __name__ == "__main__":
    run_bot()
