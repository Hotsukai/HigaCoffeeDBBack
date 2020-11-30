from logging import log
import flask
from main import app, db, bcrypt
from main.models import Entry  ,User
from main.utils import *
from flask_login import LoginManager, login_user, logout_user, login_required

@app.route('/')
def helloworld():
    return 'Hello, World!'


@app.route('/', methods=['POST'])
def oumugaeshi():
    return flask.request.get_data(), 418


@app.route('/entries/')
def show_entries():
    entries = Entry.query.all()  # 追加
    return flask.jsonify(convert_entries_to_json(entries))


@app.route('/entries/add', methods=['POST'])
#TODO: ログイン
#TODO: エラーハンドリング
def add_entry():
    new_entry_json = flask.request.json
    entry = Entry(
        title=new_entry_json['title'],
        text=new_entry_json['text']
    )
    db.session.add(entry)
    db.session.commit()
    print("data pushed", new_entry_json)
    return flask.jsonify({"message": "data pushed"})

#user Create
@app.route('/auth/create_user/', methods=['POST'])
def create_user():
    form_data = flask.request.json
    username = form_data['username']
    password = form_data['password']
    # TODO:有効な文字列か確認。
    if not username:
        return flask.jsonify({"message": "ユーザー名は必須です"}), 400
    if not password:
        return flask.jsonify({"message": "パスワードは必須です"}), 400
    users = User.query.filter_by(name = username).all()
    if len(users)!=0:
        return flask.jsonify({"message": "ユーザー名が利用されています。"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(name=username, encrypted_password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return flask.jsonify({"message": "ユーザー("+username+")を作成しました。"})
#user index TODO:
#user show
#user update 
@app.route('/auth/login/', methods=['POST'])
def login():
    form_data = flask.request.json
    username = form_data['username']
    password = form_data['password']
    # TODO:有効な文字列か確認。
    if not username:
        return flask.jsonify({"message": "ユーザー名は必須です"}), 400
    if not password:
        return flask.jsonify({"message": "パスワードは必須です"}), 400
    user = User.query.filter_by(name = username).first()
    if user and bcrypt.check_password_hash(user.encrypted_password, password):
        #ログイン成功
        login_user(user)
        print("ログイン成功")
        return flask.jsonify({"message": "ユーザー("+username+")のログインに成功しました。"})
    else:
        print("ログイン失敗")
        return flask.jsonify({"message": "ユーザー("+username+")のログインに失敗しました。"})
        