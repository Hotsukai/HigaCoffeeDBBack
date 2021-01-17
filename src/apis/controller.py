from flask import request, jsonify, Blueprint

from src.models.models import BEANS, EXTRACTION_METHOD

app = Blueprint('controller', __name__)


@app.route('/')
def helloworld():
    return 'Hello, World! こんにちは'


@app.route('/', methods=['POST'])
def oumugaeshi():
    return request.get_data(), 418


@ app.route("/beans", methods=['GET'])
def get_beans():
    return jsonify({"result": True, "data": [bean.to_json() for bean in BEANS]})


@ app.route("/extraction_methods", methods=['GET'])
def get_extraction_methods():
    return jsonify({"result": True, "data": EXTRACTION_METHOD})
