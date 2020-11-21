import flask
from main import app,db
from main.models import Entry # 追加
from main.toJson import *

@app.route('/')
def helloworld():
    return 'Hello, World!'

@app.route('/',methods=['POST'])
def oumugaeshi():
    return flask.request.get_data()

@app.route('/entries/')
def show_entries():
    entries = Entry.query.all() # 追加
    return convert_entries_to_json(entries)

@app.route('/entries/add',methods=['POST'])
#TODO: ログイン
#TODO: エラーハンドリング
def add_entry():
    new_entry_json=flask.request.json
    entry = Entry(
        title = new_entry_json['title'],
        text = new_entry_json['text']
    )
    db.session.add(entry)
    db.session.commit()
    print("data pushed",new_entry_json)
    return "data pushed"