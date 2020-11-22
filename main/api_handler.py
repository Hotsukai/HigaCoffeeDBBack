import flask
from main import app, db, bcrypt
from main.models import Entry  ,User
from main.utils import *


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
    users = db.session.query(User).\
        filter(User.name == username).\
        all()
    if len(users)!=0:
        return flask.jsonify({"message": "ユーザー名が利用されています。"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(name=username, encrypted_password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return flask.jsonify({"message": "ユーザー("+username+")を作成しました。"})
