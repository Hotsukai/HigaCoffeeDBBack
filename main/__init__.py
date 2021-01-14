# import main した時実行される
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager
)
import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
app = Flask(__name__)
app.config.from_object('main.config')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)
jwt = JWTManager(app)
ALLOW_ORIGIN = os.environ.get('ALLOW_ORIGIN')
WATCH_WORD = os.environ.get("WATCH_WORD")


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', ALLOW_ORIGIN)
    response.headers.add('Access-Control-Allow-Credentials', "true")
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


from main.controllers import controller
