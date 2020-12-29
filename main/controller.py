import flask
import datetime
from main import app, db
from main.models import BEAN, EXTRACTION_METHOD, MESH
from main.utils import *
from main.controllers import (
    users_controller, coffees_controller, reviews_controller, data_controller)

app.register_blueprint(users_controller.app)
app.register_blueprint(coffees_controller.app)
app.register_blueprint(reviews_controller.app)
app.register_blueprint(data_controller.app)


@app.route('/')
def helloworld():
    return 'Hello, World! こんにちは'


@app.route('/', methods=['POST'])
def oumugaeshi():
    return flask.request.get_data(), 418


@ app.route("/beans", methods=['GET'])
def get_beans():
    return flask.jsonify({"result": True, "data": BEAN})


@ app.route("/extraction_methods", methods=['GET'])
def get_extraction_methods():
    return flask.jsonify({"result": True, "data": EXTRACTION_METHOD})
