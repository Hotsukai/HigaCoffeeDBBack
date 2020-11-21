# import main した時実行される
from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
app = Flask(__name__)
app.config.from_object('main.config') 
app.config["JSON_AS_ASCII"] = False

db = SQLAlchemy(app) 

import main.api_handler 