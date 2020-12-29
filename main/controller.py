import flask
import datetime
from main import app, db, bcrypt, jwt
from main.models import Coffee, User, Review, BEAN, EXTRACTION_METHOD, MESH
from main.utils import *
from main.controllers import (users_controller,coffees_controller)
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, jwt_optional
)

app.register_blueprint(users_controller.app)
app.register_blueprint(coffees_controller.app)


@app.route('/')
def helloworld():
    return 'Hello, World! こんにちは'


@app.route('/', methods=['POST'])
def oumugaeshi():
    return flask.request.get_data(), 418



@app.route("/reviews", methods=['GET'])
@jwt_optional
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
    return flask.jsonify({"result": True, "data": convert_reviews_to_json(reviews, with_user=get_jwt_identity())})


@app.route("/reviews", methods=['POST'])
@jwt_required
def create_review():
    current_user = User.query.filter_by(name=get_jwt_identity()).one_or_none()
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
        if not list(filter(lambda drinker: drinker.id == reviewer_id, coffee.drinkers)):
            return flask.jsonify({"result": False, "message": "このコーヒーへのレビューを書く権利がありません"})
        if list(filter(lambda review: review.reviewer_id == reviewer_id, coffee.reviews)):
            return flask.jsonify({"result": False, "message": "このコーヒーにはすでにレビューが書かれています"})
        if len(coffee.reviews) >= len(coffee.drinkers):
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
@jwt_optional
def get_provide_count():
    data = {}
    for bean in BEAN.values():
        bean_data = {"id": bean["id"], "name": bean["name"]}
        bean_data["dripCount"] = Coffee.query.filter_by(
            bean_id=bean["id"]).count()
        bean_data["reviewCount"] = Review.query.filter(
            Review.coffee.has(bean_id=bean["id"])).count()
        current_user = User.query.filter_by(
            name=get_jwt_identity()).one_or_none()
        if current_user:
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
@jwt_optional
def get_strongness(bean_id):
    strongness_data = {}
    for strongness in range(1, 5):
        avg = db.session.query(
            db.func.avg(Coffee.extraction_time).label('time'),
            db.func.avg(Coffee.powder_amount).label('powder'),
            db.func.avg(Coffee.water_amount).label('water')
        ).filter(
            db.and_(
                Coffee.bean_id == bean_id,
                Review.coffee_id == Coffee.id,
                strongness - 1 <= Review.strongness,
                Review.strongness < strongness)
        ).one_or_none()._asdict()
        avg_ex_time = float(avg["time"]) if avg["time"] else None
        avg_powder_per_120cc = float(avg["powder"])/float(
            avg["water"])*120 if avg["water"] and avg["powder"] and float(avg["water"]) != 0 else None
        strongness_data[strongness] = {
            "averageExtractionTime": avg_ex_time,
            "averagePowderAmountPer120cc": avg_powder_per_120cc}
    current_user = User.query.filter_by(name=get_jwt_identity()).one_or_none()
    if current_user:
        for strongness in range(1, 5):
            avg = db.session.query(
                db.func.avg(Coffee.extraction_time).label('time'),
                db.func.avg(Coffee.powder_amount).label('powder'),
                db.func.avg(Coffee.water_amount).label('water')
            ).filter(
                db.and_(
                    Coffee.bean_id == bean_id,
                    Review.coffee_id == Coffee.id,
                    strongness - 1 <= Review.strongness,
                    Review.strongness < strongness,
                    Review.reviewer == current_user)
            ).one_or_none()._asdict()
            avg_ex_time = float(avg["time"]) if avg["time"] else None
            avg_powder_per_120cc = float(avg["powder"])/float(
                avg["water"])*120 if avg["water"] and avg["powder"] and float(avg["water"]) != 0 else None
            strongness_data[strongness].update({
                "usersAverageExtractionTime": avg_ex_time,
                "usersAveragePowderAmountPer120cc": avg_powder_per_120cc})
    return flask.jsonify({"result": True, "data": strongness_data})


@ app.route("/data/bean_position")
@jwt_optional
def get_position():
    position_data = {}
    for bean_id in BEAN.keys():
        avg = db.session.query(
            db.func.avg(Review.bitterness).label('bitterness'),
            db.func.avg(Review.strongness).label('strongness'),
            db.func.avg(Review.situation).label('situation'),
            db.func.avg(Review.want_repeat).label('want_repeat')
        ).filter(Coffee.bean_id == bean_id).filter(Review.coffee_id == Coffee.id).one_or_none()._asdict()
        avg_bitterness = float(
            avg['bitterness']) if avg['bitterness'] else None
        avg_strongness = float(
            avg['strongness']) if avg['strongness'] else None
        avg_situation = float(avg['situation']) if avg['situation'] else None
        avg_want_repeat = float(
            avg['want_repeat']) if avg['want_repeat'] else None
        position_data[bean_id] = {
            'avgBitterness': avg_bitterness,
            'avgStrongness': avg_strongness,
            'avgSituation': avg_situation,
            'avgWantRepeat': avg_want_repeat,
            "beanName": BEAN[bean_id]["name"]
        }
    current_user = User.query.filter_by(name=get_jwt_identity()).one_or_none()
    if current_user:
        for bean_id in BEAN.keys():
            avg = db.session.query(
                db.func.avg(Review.bitterness).label('bitterness'),
                db.func.avg(Review.strongness).label('strongness'),
                db.func.avg(Review.situation).label('situation'),
                db.func.avg(Review.want_repeat).label('want_repeat')
            ).filter(Coffee.bean_id == bean_id)\
                .filter(Review.coffee_id == Coffee.id)\
                .filter(Review.reviewer_id == current_user.id)\
                .one_or_none()._asdict()
            avg_bitterness = float(
                avg['bitterness']) if avg['bitterness'] else None
            avg_strongness = float(
                avg['strongness']) if avg['strongness'] else None
            avg_situation = float(
                avg['situation']) if avg['situation'] else None
            avg_want_repeat = float(
                avg['want_repeat']) if avg['want_repeat'] else None
            position_data[bean_id].update({
                'usersAvgBitterness': avg_bitterness,
                'usersAvgStrongness': avg_strongness,
                'usersAvgSituation': avg_situation,
                'usersAvgWantRepeat': avg_want_repeat,
            })
    return flask.jsonify({"result": True, "data": position_data})
