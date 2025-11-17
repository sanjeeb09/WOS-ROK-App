from flask import Flask
from threading import Thread
import logging

# 1. Disable Flask internal logging. 
# THIS LINE FIXES THE "OUTPUT TOO LARGE" ERROR.
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('')

@app.route('/')
def home():
    # 2. Return a tiny string to satisfy Cronjobs
    return "Alive."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
