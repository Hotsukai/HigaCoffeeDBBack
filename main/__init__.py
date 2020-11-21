# import main した時実行される
from flask import Flask
from flask_sqlalchemy import SQLAlchemy # 追加
app = Flask(__name__)
app.config.from_object('main.config') # 追加

db = SQLAlchemy(app) # 追加

import main.api_handler 