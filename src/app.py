import os
from os.path import join, dirname

from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from src.database import init_db


load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def create_app():
    app = Flask(__name__)
    app.config.from_object('src.config.Config')
    init_db(app)
    CORS(app)
    return app


app = create_app()
jwt = JWTManager(app)
WATCH_WORD = os.environ.get("WATCH_WORD")
bcrypt = Bcrypt(app)

from src.apis import (controller, users_controller,
                      coffees_controller, reviews_controller,
                      data_controller)

app.register_blueprint(controller.app)
app.register_blueprint(coffees_controller.app)
app.register_blueprint(users_controller.app)
app.register_blueprint(reviews_controller.app)
app.register_blueprint(data_controller.app)
