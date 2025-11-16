from flask import Flask  # <--- THIS LINE WAS MISSING OR BROKEN
from threading import Thread
import logging

# Disable Flask internal logging to prevent console spam
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('')

@app.route('/')
def home():
    return "Alive."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()