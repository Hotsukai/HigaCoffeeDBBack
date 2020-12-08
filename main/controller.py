from logging import log
from os import name
import flask
from main import app, db, bcrypt, login_manager, WATCH_WORD, ALLOW_ORIGIN
from main.models import Coffee, User, Review, BEAN, EXTRACTION_METHOD, MESH
from main.utils import *
from flask_login import login_user, logout_user, login_required, current_user


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', ALLOW_ORIGIN)
    response.headers.add('Access-Control-Allow-Credentials', "true")
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).one_or_none()


@app.route('/')
def helloworld():
    return 'Hello, World! こんにちは'


@app.route('/', methods=['POST'])
def oumugaeshi():
    return flask.request.get_data(), 418


# user Create
@app.route('/auth/create_user', methods=['POST'])
def create_user():
    form_data = flask.request.json
    username = form_data.get('username')
    password = form_data.get('password')
    profile = form_data.get('profile')
    watchword = form_data.get('watchword')
    if watchword != WATCH_WORD:
        return flask.jsonify({"message": "合言葉が違います"}), 400
    # TODO:有効な文字列か確認。
    if not username:
        return flask.jsonify({"message": "ユーザー名は必須です"}), 400
    if not password:
        return flask.jsonify({"message": "パスワードは必須です"}), 400
    if User.query.filter_by(name=username).one_or_none():
        return flask.jsonify({"message": "ユーザー名が利用されています。"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(name=username, encrypted_password=hashed_password,
                profile=profile)
    db.session.add(user)
    db.session.commit()
    return flask.jsonify({"message": "ユーザー("+username+")を作成しました。"})

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
        # ログイン成功
        login_user(user)
        print("ログイン成功")
        return flask.jsonify({"result": True, "message": "ユーザー("+username+")のログインに成功しました。", "data": convert_user_to_json(user)})
    else:
        print("ログイン失敗")
        return flask.jsonify({"result": False, "message": "ユーザー("+username+")のパスワードが間違っています"})


@app.route("/auth", methods=['GET'])
def auth():
    if current_user.is_authenticated:
        print("current_user : "+current_user.name)
        return flask.jsonify({"result": True, "data": convert_user_to_json(current_user), "message": "現在のユーザーです"})
    else:
        print("ログインされていません")
        return flask.jsonify({"result": False, "data": None, "message": "ログインされていません"})


@app.route("/users", methods=['GET'])
@login_required
def get_users():
    name = flask.request.args.get('name', type=str)
    users = []
    if name is not None:
        users = User.query.filter(User.name == name).limit(50).all()
    else:
        users = User.query.limit(50).all()
    data = []
    for user in users:
        data.append({"name": user.name, "id": user.id})
    return flask.jsonify({"result": True, "message": None, "data": data})


@app.route("/coffees", methods=['GET'])
def get_coffees():
    sql_query = []
    has_review = flask.request.args.get('has_review', type=str)
    dripper_id = flask.request.args.get('dripper_id', type=int)
    drinker_id = flask.request.args.get('drinker_id', type=int)
    bean_id = flask.request.args.get('bean_id', type=int)
    print("has_review : ", has_review,
          "dripper_id : ", dripper_id,
          "drinker_id : ", drinker_id,
          "bean_id : ", bean_id)
    if dripper_id is not None:
        sql_query.append(Coffee.dripper_id ==
                         dripper_id)
    if drinker_id is not None:
        sql_query.append(Coffee.drinker_id == drinker_id)
    if bean_id is not None:
        sql_query.append(Coffee.bean_id == bean_id)
    if has_review == "true":
        sql_query.append(Coffee.review_id != None)
    elif has_review == "false":
        sql_query.append(Coffee.review_id == None)

    coffees = Coffee.query.filter(db.and_(*sql_query)).limit(50).all()
    print("coffees : ", coffees)

    return flask.jsonify(convert_coffees_to_json(coffees))


@app.route("/coffees", methods=['POST'])
@login_required
def create_coffee():
    form_data = flask.request.json
    if current_user.id != form_data.get('dripperId'):
        return flask.jsonify({"result": False, "message": "ユーザが不正です"})
    bean_id = form_data.get('beanId')
    dripper_id = current_user.id
    extraction_time = form_data.get('extractionTime')
    extraction_method_id = form_data.get('extractionMethodId')
    mesh_id = form_data.get('meshId')
    memo = form_data.get('memo')
    powder_amount = form_data.get("powderAmount")
    water_amount = form_data.get('waterAmount')
    water_temperature = form_data.get('waterTemperature')
    new_coffee = Coffee(bean_id=bean_id,  dripper_id=dripper_id,
                        extraction_time=extraction_time, extraction_method_id=extraction_method_id,
                        mesh_id=mesh_id, memo=memo, powder_amount=powder_amount, water_amount=water_amount, water_temperature=water_temperature, )
    db.session.add(new_coffee)
    for drinker_id in form_data.get('drinkerIds'):
        print("drinkerId",drinker_id)
        drinker = User.query.filter_by(id=drinker_id).one_or_none()
        print("drinker : ",drinker)
        new_coffee.drinker.append(drinker)
    db.session.commit()
    return flask.jsonify({"result": True, "message": "コーヒーを作成しました。", "data": convert_coffee_to_json(new_coffee)})


@app.route("/reviews", methods=['GET'])
def get_reviews():
    reviewer_id = flask.request.args.get('reviewer', type=int)
    if reviewer_id is not None:
        user = User.query.get(reviewer_id)
        if user is not None:
            reviews = user.reviews
            return flask.jsonify({"result": True, "data": convert_reviews_to_json(reviews)})
    return flask.jsonify({"result": False, "data": None})


@app.route("/reviews", methods=['POST'])
@login_required
def create_review():
    form_data = flask.request.json

    bitterness = form_data.get('bitterness')
    coffee_id = form_data.get('coffee_id')
    feeling = form_data.get('feeling')
    reviewer_id = current_user.id
    situation = form_data.get('situation')
    strongness = form_data.get('strongness')
    want_repeat = form_data.get('wantRepeat')

    new_review = Review(bitterness=bitterness, want_repeat=want_repeat, coffee_id=coffee_id,
                        situation=situation, strongness=strongness, feeling=feeling, reviewer_id=reviewer_id)
    db.session.add(new_review)
    db.session.commit()
    return flask.jsonify({"result": True, "message": "レビューを作成しました。", "data": convert_review_to_json(new_review)})
# TODO: queries,limit


@app.route("/beans", methods=['GET'])
def get_beans():
    return flask.jsonify({"result": True, "data": BEAN})


@app.route("/extraction_methods", methods=['GET'])
def get_extraction_methods():
    return flask.jsonify({"result": True, "data": EXTRACTION_METHOD})
