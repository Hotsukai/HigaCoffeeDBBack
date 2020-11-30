# import main した時実行される
from logging import log
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
app = Flask(__name__)
app.config.from_object('main.config') 

app.config["JSON_AS_ASCII"] = False

db = SQLAlchemy(app) 
bcrypt = Bcrypt(app)  
login_manager = LoginManager()
login_manager.init_app(app)

import main.api_handler 