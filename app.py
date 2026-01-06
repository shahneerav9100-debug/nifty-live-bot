import os
import threading
from flask import Flask
import main # your bot file

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Bot is Running!</h1><p>Check your Telegram.</p>"

# This is a secret test link. Visit your-url.onrender.com/test to force a message.
@app.route('/test')
def test():
    main.send_telegram("🔔 MANUAL TEST: I received your click from the browser!")
    return "Test message sent to Telegram!"

if __name__ == "__main__":
    # Start bot thread
    threading.Thread(target=main.run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
