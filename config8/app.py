
from flask import Flask
app = Flask('config8')

@app.route('/')
def index():
    return "harro"
