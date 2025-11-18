from flask import Flask
from threading import Thread
import logging
import os  # <--- THIS IS NEW AND IMPORTANT

# Silence the logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('')

@app.route('/')
def home():
    return "Alive."

def run():
    # Get the PORT from Render automatically, or use 8080 if testing locally
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
