from flask import Flask
import threading
import main 
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot logic is triggered!"

if __name__ == "__main__":
    # This starts your trading logic in the background
    threading.Thread(target=main.run_bot, daemon=True).start()
    # Render uses port 10000 by default
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
