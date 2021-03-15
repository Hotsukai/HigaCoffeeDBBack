from flask import jsonify
from src.models.models import User
from src.app import jwt


@jwt.unauthorized_loader
def my_expired_token_callback(reason):
    return jsonify({"result": False, "message": "ログインが必要です", "data": {}}), 401


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.name


@jwt.user_lookup_loader
def user_loader_callback(header, payload):
    return User.query.filter_by(name=payload)
