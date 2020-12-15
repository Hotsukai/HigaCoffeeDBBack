from logging import log
from os import name
import flask
from main import app, db, bcrypt, login_manager, WATCH_WORD, ALLOW_ORIGIN
from main.models import Coffee, User, Review, BEAN, EXTRACTION_METHOD, MESH
from main.utils import *
from flask_login import login_user, logout_user, login_required, current_user
# TODO:テスト書く


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
        print(watchword, WATCH_WORD)
        return flask.jsonify({"result": False, "message": "合言葉が違います"})
    # TODO:有効な文字列か確認。
    if not username:
        return flask.jsonify({"result": False, "message": "ユーザー名は必須です"})
    if not password:
        return flask.jsonify({"result": False, "message": "パスワードは必須です"})
    if User.query.filter_by(name=username).one_or_none():
        return flask.jsonify({"result": False, "message": "ユーザー名が利用されています。"})

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(name=username, encrypted_password=hashed_password,
                profile=profile)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return flask.jsonify({"result": True, "message": "ユーザー("+username+")を作成しました。", "data": convert_user_to_json(user)})

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
        login_user(user)
        return flask.jsonify({"result": True, "message": "ユーザー("+username+")のログインに成功しました。", "data": convert_user_to_json(user)})
    else:
        return flask.jsonify({"result": False, "message": "ユーザー("+username+")のパスワードが間違っています"})


@app.route('/auth/logout')
@login_required
def logout():
    logout_user()
    return flask.jsonify({"result": True, "message": "ログアウトしました"})


@app.route("/auth", methods=['GET'])
def auth():
    if current_user.is_authenticated:
        return flask.jsonify({"result": True, "data": convert_user_to_json(current_user), "message": "現在のユーザーです"})
    else:
        return flask.jsonify({"result": False, "data": None, "message": "ログインされていません"})


@app.route("/users", methods=['GET'])
@login_required
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


@app.route("/coffees", methods=['GET'])
def get_coffees():
    sql_query = []
    has_review = flask.request.args.get('has_review', type=str)
    dripper_id = flask.request.args.get('dripper_id', type=int)
    drinker_id = flask.request.args.get('drinker_id', type=int)
    bean_id = flask.request.args.get('bean_id', type=int)

    if dripper_id is not None:
        if current_user.is_authenticated and dripper_id is current_user.id:
            sql_query.append(Coffee.dripper_id == dripper_id)
        else:
            return flask.jsonify({"result": False, "message": "ログインしてください"}), 401
    if drinker_id is not None:
        if current_user.is_authenticated and drinker_id is current_user.id:
            if has_review == "true":
                sql_query.append(Coffee.drinker.any(id=drinker_id))
                sql_query.append(Coffee.reviews.any(reviewer_id=drinker_id))
            elif has_review == "false":
                sql_query.append(Coffee.drinker.any(id=drinker_id))
                sql_query.append(~ Coffee.reviews.any(reviewer_id=drinker_id))
        else:
            return flask.jsonify({"result": False, "message": "ログインしてください"}), 401
    if bean_id is not None:
        sql_query.append(Coffee.bean_id == bean_id)

    coffees = Coffee.query.filter(
        db.and_(*sql_query)).order_by(db.desc(Coffee.created_at)).limit(50).all()
    return flask.jsonify({"result": True, "data": convert_coffees_to_json(coffees)})


@app.route("/coffees/<int:id>", methods=['GET'])
def get_coffee(id):
    coffee = Coffee.query.get(id)
    return flask.jsonify({"result": True, "data": convert_coffee_to_json(coffee)})


@app.route("/coffees", methods=['POST'])
@login_required
def create_coffee():
    form_data = flask.request.json
    if current_user.id != form_data.get('dripperId'):
        return flask.jsonify({"result": False, "message": "ユーザが不正です"}), 401
    bean_id = form_data.get('beanId')
    dripper_id = current_user.id
    extraction_time = form_data.get('extractionTime')
    extraction_method_id = form_data.get('extractionMethodId')
    mesh_id = form_data.get('meshId')
    memo = form_data.get('memo')
    powder_amount = form_data.get("powderAmount")
    water_amount = form_data.get('waterAmount')
    water_temperature = form_data.get('waterTemperature')
    if extraction_time > 10 or extraction_time <= 0 or\
            powder_amount > 20 or powder_amount <= 0 or \
            water_amount <= 0 or water_amount > 500 or\
            water_temperature > 100 or water_temperature < 0:
        return flask.jsonify({"result": False, "message": "入力が不正です"})
    new_coffee = Coffee(bean_id=bean_id,  dripper_id=dripper_id,
                        extraction_time=extraction_time, extraction_method_id=extraction_method_id,
                        mesh_id=mesh_id, memo=memo, powder_amount=powder_amount, water_amount=water_amount, water_temperature=water_temperature, )
    db.session.add(new_coffee)
    drinkers = []
    for id in form_data.get('drinkerIds'):
        if id != None and id != "":
            drinkers.append(int(id))

    drinkers = list(set(drinkers))
    if len(drinkers) == 0:
        return flask.jsonify({"result": False, "mesage": "飲む人を指定してください"})
    for drinker_id in drinkers:
        drinker = User.query.filter_by(id=drinker_id).one_or_none()
        new_coffee.drinker.append(drinker)
    db.session.commit()
    return flask.jsonify({"result": True, "message": "コーヒーを作成しました。", "data": convert_coffee_to_json(new_coffee, True)})

# TODO:ページネーション


@app.route("/reviews", methods=['GET'])
def get_reviews():
    sql_query = []
    reviewer_id = flask.request.args.get('reviewer', type=int)
    bean_ids = flask.request.args.get('beans')
    bean_ids = bean_ids.split(",") if bean_ids else None
    if reviewer_id:
        user = User.query.get(reviewer_id)
        if user is not None:
            sql_query.append(Review.reviewer.has(id=reviewer_id))
    if bean_ids:
        bean_query = []
        for bean_id in bean_ids:
            bean_query.append(Review.coffee.has(bean_id=bean_id))
        sql_query.append(db.or_(*bean_query))
    reviews = Review.query.filter(
        db.and_(*sql_query)).order_by(db.desc(Review.created_at)).limit(50).all()

    return flask.jsonify({"result": True, "data": convert_reviews_to_json(reviews, with_user=current_user.is_active)})


@app.route("/reviews", methods=['POST'])
@login_required
def create_review():
    try:
        form_data = flask.request.json
        if current_user.id != form_data.get('reviewerId'):
            return flask.jsonify({"result": False, "message": "ユーザが不正です"}), 401
        bitterness = form_data.get('bitterness')
        coffee_id = form_data.get('coffeeId')
        feeling = form_data.get('feeling')
        situation = form_data.get('situation')
        strongness = form_data.get('strongness')
        reviewer_id = current_user.id
        want_repeat = form_data.get('wantRepeat')
        if bitterness > 4 or bitterness < 0 or strongness > 4 or strongness < 0 or situation > 4 or situation < 0 or want_repeat > 3 or want_repeat < 0:
            return flask.jsonify({"result": False, "message": "入力が不正です"})
        new_review = Review(bitterness=bitterness, want_repeat=want_repeat, coffee_id=coffee_id,
                            situation=situation, strongness=strongness, feeling=feeling, reviewer_id=reviewer_id)
        coffee = Coffee.query.get(coffee_id)
        if not list(filter(lambda drinker: drinker.id == reviewer_id, coffee.drinker)):
            return flask.jsonify({"result": False, "message": "このコーヒーへのレビューを書く権利がありません"})
        if list(filter(lambda review: review.reviewer_id == reviewer_id, coffee.reviews)):
            return flask.jsonify({"result": False, "message": "このコーヒーにはすでにレビューが書かれています"})
        if len(coffee.reviews) >= len(coffee.drinker):
            return flask.jsonify({"result": False, "message": "このコーヒーにはすでにレビューが書かれています"})

        db.session.add(new_review)
        coffee.reviews.append(new_review)
        db.session.commit()
        return flask.jsonify({"result": True, "message": "レビューを作成しました。", "data": convert_review_to_json(new_review)})
    except Exception as e:
        print(e)
        return flask.jsonify({"result": False, "message": "予期せぬエラーが発生しました : {}".format(e)}), 500


@ app.route("/beans", methods=['GET'])
def get_beans():
    return flask.jsonify({"result": True, "data": BEAN})


@ app.route("/extraction_methods", methods=['GET'])
def get_extraction_methods():
    return flask.jsonify({"result": True, "data": EXTRACTION_METHOD})


@app.route("/data/provide", methods=['GET'])
def get_provide_count():
    data = {}
    for bean in BEAN.values():
        print("bean", bean)
        bean_data = {"id": bean["id"], "name": bean["name"]}

        bean_data["dripCount"] = Coffee.query.filter_by(
            bean_id=bean["id"]).count()
        bean_data["reviewCount"] = Review.query.filter(
            Review.coffee.has(bean_id=bean["id"])).count()
        if current_user.is_active:
            bean_data["usersDripCount"] = Coffee.query.filter(
                db.and_(
                    Coffee.bean_id == bean["id"],
                    Coffee.dripper_id == current_user.id))\
                .count()
            bean_data["usersReviewCount"] = Review.query.filter(
                db.and_(
                    Review.coffee.has(bean_id=bean["id"]),
                    Review.reviewer_id == current_user.id))\
                .count()
        data[bean["id"]] = bean_data
    return flask.jsonify({"result": True, "data": data})


@app.route("/data/strongness/<int:bean_id>")
def get_bitterness(bean_id):
    strongness_data = {}
    for strongness in range(1, 5):
        avg = db.session.query(
            db.func.avg(Coffee.extraction_time).label('time'),
            db.func.avg(Coffee.powder_amount).label('powder'),
            db.func.avg(Coffee.water_amount).label('water')
        ).filter(
            db.and_(
                Coffee.bean_id == bean_id,
                Review.strongness == strongness)
        ).one_or_none()._asdict()

        avg_ex_time = float(avg["time"]) if avg["time"] else None
        avg_powder_per_120cc = float(avg["powder"])/float(
            avg["water"])*120 if avg["water"] and avg["powder"] and float(avg["water"]) != 0 else None
        strongness_data[strongness] = {
            "average_extraction_time": avg_ex_time,
            "average_powder_amount_per_120cc": avg_powder_per_120cc}
    print(strongness_data)
    return flask.jsonify({"result": True, "data": strongness_data})


@ app.route("/data/bean_position")
def get_position():
    position_data = {}
    for bean_id in BEAN.keys():
        avg = db.session.query(
            db.func.avg(Review.bitterness).label('bitterness'),
            db.func.avg(Review.strongness).label('strongness'),
            db.func.avg(Review.situation).label('situation'),
            db.func.avg(Review.want_repeat).label('want_repeat')
        ).filter(Coffee.bean_id == bean_id)\
            .one_or_none()._asdict()
        avg_bitterness = float(
            avg['bitterness']) if avg['bitterness'] else None
        avg_strongness = float(
            avg['strongness']) if avg['strongness'] else None
        avg_situation = float(avg['situation']) if avg['situation'] else None
        avg_want_repeat = float(
            avg['want_repeat']) if avg['want_repeat'] else None
        position_data[bean_id] = {
            'avg_bitterness': avg_bitterness,
            'avg_strongness': avg_strongness,
            'avg_situation': avg_situation,
            'avg_want_repeat': avg_want_repeat,

        }
    return flask.jsonify({"result": True, "data": position_data})
