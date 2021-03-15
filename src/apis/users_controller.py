from typing import List

import flask
from flask_jwt_extended import (jwt_required, create_access_token,
                                get_jwt_identity)

from src.app import bcrypt, WATCH_WORD
from src.database import db
from src.models.models import User

app = flask.Blueprint('users_controller', __name__)


# user Create
@app.route('/auth/create_user', methods=['POST'])
def create_user():
    form_data = flask.request.json
    username: str = form_data.get('username')
    password: str = form_data.get('password')
    profile: str = form_data.get('profile')
    watchword: str = form_data.get('watchword')
    if watchword != WATCH_WORD:
        return flask.jsonify({"result": False, "message": "合言葉が違います"}), 401
    # TODO:有効な文字列か確認。
    if not username:
        return flask.jsonify({"result": False, "message": "ユーザー名は必須です"}), 400
    if len(username) > 30:
        return flask.jsonify({"result": False, "message": "ユーザー名が長すぎます"}), 400
    if not password:
        return flask.jsonify({"result": False, "message": "パスワードは必須です"}), 400
    if len(password.encode('utf-8')) > 50:
        return flask.jsonify({"result": False, "message": "パスワードが長すぎます"}), 400
    if User.query.filter_by(name=username).one_or_none():
        return flask.jsonify({
            "result": False,
            "message": "ユーザー名が利用されています"
        }), 409
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user: User = User(name=username,
                      encrypted_password=hashed_password,
                      profile=profile)
    db.session.add(user)
    db.session.commit()
    access_token: str = create_access_token(identity=user)
    return flask.jsonify({
        "result": True,
        "message": "ユーザー(" + username + ")を作成しました。",
        "data": user.to_json(),
        'token': access_token
    }), 201


# TODO:エラーハンドリング


# ユーザー名変更
@app.route('/auth/changeUsername', methods=['POST'])
def change_username():
    form_data = flask.request.json
    current_username: str = form_data.get('currentUsername')
    new_username: str = form_data.get('newUsername')
    password: str = form_data.get('password')
    if not new_username:
        return flask.jsonify({
            "result": False,
            "message": "新しいユーザー名は必須です"
        }), 400
    if len(new_username) > 30:
        return flask.jsonify({"result": False, "message": "ユーザー名が長すぎます"}), 400
    if not password:
        return flask.jsonify({
            "result": False,
            "message": "パスワードを入力してください"
        }), 400
    if User.query.filter_by(name=new_username).one_or_none():
        return flask.jsonify({
            "result": False,
            "message": "新しいユーザー名は既に利用されています"
        }), 409

    user: User = User.query.filter_by(name=current_username).one_or_none()
    # 現在のユーザー名で登録されているかの確認
    if user is None:
        return flask.jsonify({
            "result":
            False,
            "message":
            "ユーザー(" + current_username + ")は登録されていません"
        }), 401

    if bcrypt.check_password_hash(user.encrypted_password, password):
        # 新しいユーザー名に更新してアクセストークンを作成
        user.name = new_username
        access_token: str = create_access_token(identity=user)

        # dbを更新
        db.session.merge(user)
        db.session.commit()

        return flask.jsonify({
            "result":
            True,
            "message":
            "ユーザー名を" + current_username + "から" + new_username + "に変更しました",
            "data":
            user.to_json(),
            'token':
            access_token
        })
    else:
        return flask.jsonify({
            "result":
            False,
            "message":
            "ユーザー(" + current_username + ")のパスワードが間違っています"
        }), 401


@app.route('/auth/login', methods=['POST'])
def login():
    form_data = flask.request.json
    username: str = form_data.get('username')
    password: str = form_data.get('password')
    if not username:
        return flask.jsonify({"result": False, "message": "ユーザー名は必須です"}), 400
    if not password:
        return flask.jsonify({"result": False, "message": "パスワードは必須です"}), 400
    user: User = User.query.filter_by(name=username).one_or_none()
    if user is None:
        return flask.jsonify({
            "result": False,
            "message": "ユーザー(" + username + ")は登録されていません"
        }), 401

    if bcrypt.check_password_hash(user.encrypted_password, password):
        access_token: str = create_access_token(identity=user)

        return flask.jsonify({
            "result": True,
            "message": "ユーザー(" + username + ")のログインに成功しました。",
            "data": user.to_json(),
            'token': access_token
        })
    else:
        return flask.jsonify({
            "result": False,
            "message": "ユーザー(" + username + ")のパスワードが間違っています"
        }), 401


# TODO: ログアウト実装
# https://flask-jwt-extended.readthedocs.io/en/stable/blacklist_and_token_revoking/
# @app.route('/auth/logout')
# @jwt_required
# def logout():
#     # logout_user()
#     return flask.jsonify({"result": True, "message": "ログアウトしました"})


@app.route("/auth", methods=['GET'])
@jwt_required(optional=True)
def auth():
    current_user: User = User.query.filter_by(name=get_jwt_identity())\
        .one_or_none()
    if current_user:
        return flask.jsonify({
            "result": True,
            "data": current_user.to_json(),
            "message": "現在のユーザーです"
        })
    else:
        return flask.jsonify({
            "result": False,
            "data": None,
            "message": "ログインされていません"
        })


@app.route("/users", methods=['GET'])
@jwt_required()
def get_users():
    name: str = flask.request.args.get('name', type=str)
    users = []
    if name is not None:
        users: List[User] = User.query.filter(User.name == name).order_by(
            db.desc(User.created_at)).limit(50).all()
    else:
        users = User.query.order_by(db.desc(User.created_at)).limit(50).all()
    data = []
    for user in users:
        data.append({"name": user.name, "id": user.id})
    return flask.jsonify({"result": True, "message": None, "data": data})


@app.route("/users/<int:id>", methods=['GET'])
@jwt_required()
def get_user(id: int):
    user: User = User.query.get(id)
    if user:
        return flask.jsonify({
            "result": True,
            "message": None,
            "data": user.to_json()
        })
    else:
        return flask.jsonify({
            "result": False,
            "message": "ユーザーが存在しません",
        }), 404


if __name__ == "__main__":
    pass
