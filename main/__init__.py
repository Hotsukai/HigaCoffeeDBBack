# import main した時実行される
from logging import log
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
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
login_manager = LoginManager()
login_manager.init_app(app)
CORS(app)
ALLOW_ORIGIN=os.environ.get('ALLOW_ORIGIN')
WATCH_WORD=os.environ.get("WATCH_WORD")

import main.controller