from os import getenv
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

def create_app():
    return app