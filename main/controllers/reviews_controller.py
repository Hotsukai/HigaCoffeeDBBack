import flask
from main import db, bcrypt, jwt
from main.models import Coffee, User, Review
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity, jwt_optional
)
app = flask.Blueprint('reviews_controller', __name__)


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
    return flask.jsonify({"result": True, "data": [review.to_json(with_user=get_jwt_identity()) for review in reviews]})


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
        return flask.jsonify({"result": True, "message": "レビューを作成しました。", "data": new_review.to_json()})
    except Exception as e:
        print(e)
        return flask.jsonify({"result": False, "message": "予期せぬエラーが発生しました : {}".format(e)}), 500
