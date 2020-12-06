from logging import log
import flask
from main import app, db, bcrypt, login_manager, WATCH_WORD, ALLOW_ORIGIN
from main.models import Coffee, User, Review, BEAN, EXTRACTION_METHOD, MESH
from main.utils import *
from flask_login import login_user, logout_user, login_required, current_user
# TODO: def checkPassフレーズ


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', ALLOW_ORIGIN)
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
# user index TODO:
# user show
# user update
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
        return flask.jsonify({"result": True, "data":convert_user_to_json(current_user),"message":"現在のユーザーです"})
    else:
        print("ログインされていません")
        return flask.jsonify({"result": False, "data":None,"message":"ログインされていません"})


@app.route("/coffees", methods=['POST'])
@login_required
def create_coffee():
    form_data = flask.request.json
    powder_amount = form_data.get("powder_amount")
    extraction_time = form_data.get('extraction_time')
    extraction_method_id = form_data.get('extraction_method_id')
    mesh_id = form_data.get('mesh_id')
    water_amount = form_data.get('water_amount')
    water_temperature = form_data.get('water_temperature')
    bean_id = form_data.get('bean_id')
    dripper_id = current_user.id
    drinker_id = form_data.get('drinker_id')
    new_coffee = Coffee(powder_amount=powder_amount, extraction_time=extraction_time, extraction_method_id=extraction_method_id,
                        mesh_id=mesh_id, water_amount=water_amount, water_temperature=water_temperature, bean_id=bean_id, dripper_id=dripper_id, drinker_id=drinker_id)
    db.session.add(new_coffee)
    db.session.commit()
    return flask.jsonify({"message": "コーヒーを作成しました。"})
# TODO: queries,limit


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

    coffees = Coffee.query.filter(db.and_(*sql_query)).all()
    print("coffees : ", coffees)

    return flask.jsonify(convert_coffees_to_json(coffees))


@app.route("/reviews", methods=['GET'])
def get_reviews():
    reviewer_id = flask.request.args.get('reviewer', type=int)
    user = {}
    # if reviewer_id is None:
    #     reviews = db.session.query(User, Review).filter
    #     user = User.query.filter_by(id=reviewer_id).one()
    # reviews = user.reviews
    reviews = Review.query.all()
    print("reviews : ", reviews)

    return flask.jsonify(convert_reviews_to_json(reviews))


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
