import flask
from flask import Blueprint
from main import app, db, bcrypt, jwt,WATCH_WORD
from main.utils import *

from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, jwt_optional
)
from main.models import User

app = Blueprint('users_controller', __name__)

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.name


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    return User.query.filter_by(name=identity)


# user Create
@app.route('/auth/create_user', methods=['POST'])
def create_user():
    form_data = flask.request.json
    username = form_data.get('username')
    password = form_data.get('password')
    profile = form_data.get('profile')
    watchword = form_data.get('watchword')
    if watchword != WATCH_WORD:
        return flask.jsonify({"result": False, "message": "合言葉が違います"})
    # TODO:有効な文字列か確認。
    if not username:
        return flask.jsonify({"result": False, "message": "ユーザー名は必須です"})
    if len(username) > 30:
        return flask.jsonify({"result": False, "message": "ユーザー名が長すぎます"})
    if not password:
        return flask.jsonify({"result": False, "message": "パスワードは必須です"})
    if len(password.encode('utf-8')) > 50:
        return flask.jsonify({"result": False, "message": "パスワードが長すぎます"})
    if User.query.filter_by(name=username).one_or_none():
        return flask.jsonify({"result": False, "message": "ユーザー名が利用されています。"})
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(name=username, encrypted_password=hashed_password,
                profile=profile)
    db.session.add(user)
    db.session.commit()
    access_token = create_access_token(identity=user)
    return flask.jsonify({"result": True, "message": "ユーザー("+username+")を作成しました。", "data": convert_user_to_json(user), 'token': access_token})

# TODO:エラーハンドリング


@app.route('/auth/login', methods=['POST'])
def login():
    form_data = flask.request.json
    username = form_data.get('username')
    password = form_data.get('password')
    # TODO:有効な文字列か確認。
    if not username:
        return flask.jsonify({"result": False, "message": "ユーザー名は必須です"})
    if not password:
        return flask.jsonify({"result": False, "message": "パスワードは必須です"})
    user = User.query.filter_by(name=username).one_or_none()
    if user is None:
        return flask.jsonify({"result": False, "message": "ユーザー("+username+")は登録されていません"})

    if bcrypt.check_password_hash(user.encrypted_password, password):
        access_token = create_access_token(identity=user)

        return flask.jsonify({"result": True, "message": "ユーザー("+username+")のログインに成功しました。",
                              "data": convert_user_to_json(user), 'token': access_token})
    else:
        return flask.jsonify({"result": False, "message": "ユーザー("+username+")のパスワードが間違っています"})

# TODO: ログアウト実装https://flask-jwt-extended.readthedocs.io/en/stable/blacklist_and_token_revoking/
# @app.route('/auth/logout')
# @jwt_required
# def logout():
#     # logout_user()
#     return flask.jsonify({"result": True, "message": "ログアウトしました"})


@app.route("/auth", methods=['GET'])
@jwt_optional
def auth():
    current_user = User.query.filter_by(name=get_jwt_identity()).one_or_none()
    if current_user:
        return flask.jsonify({"result": True, "data": convert_user_to_json(current_user), "message": "現在のユーザーです"})
    else:
        return flask.jsonify({"result": False, "data": None, "message": "ログインされていません"})


@app.route("/users", methods=['GET'])
@jwt_required
def get_users():
    name = flask.request.args.get('name', type=str)
    users = []
    if name is not None:
        users = User.query.filter(User.name == name).order_by(
            db.desc(User.created_at)).limit(50).all()
    else:
        users = User.query.order_by(db.desc(User.created_at)).limit(50).all()
    data = []
    for user in users:
        data.append({"name": user.name, "id": user.id})
    return flask.jsonify({"result": True, "message": None, "data": data})
