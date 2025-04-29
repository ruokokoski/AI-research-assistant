from flask import (
    render_template
)
from config import app

@app.route("/")
def render_home():
    return render_template("index.html")

@app.route("/ping")
def ping():
    return "Pong"