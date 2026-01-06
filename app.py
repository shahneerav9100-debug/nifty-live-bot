from flask import Flask
import threading
import main 
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "The Web Server is Online!"

if __name__ == "__main__":
    # This starts the run_bot function from main.py
    threading.Thread(target=main.run_bot, daemon=True).start()
    
    # This starts the web server for Render/Cron-job
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
