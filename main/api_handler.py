import flask 
from main import app
from main.models import Entry # 追加
from main.toJson import *

@app.route('/')
def helloworld():
    return 'Hello, World!'

@app.route('/entries')
def show_entries():
    entries = Entry.query.all() # 追加
    print(entries)
    # todo: tojson
    print(convert_entries_to_json(entries))
    return convert_entries_to_json(entries)