from flask import Flask
import threading
from main import run_bot

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is alive!"

if __name__ == "__main__":
    # Start the Nifty bot in a separate thread so the web server can run
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)