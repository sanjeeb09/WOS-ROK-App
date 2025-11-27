from flask import Flask
from threading import Thread
import logging
import os

# 1. Silence Flask logs so they don't spam your console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('')

@app.route('/')
def home():
    return "Alive."

def run():
    # 2. Get the PORT from Render automatically, or use 8080 if testing locally
    # This prevents the "Web Service Failed" error on deployment
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    # 3. daemon=True ensures this thread dies when the main bot quits
    t = Thread(target=run, daemon=True)
    t.start()
