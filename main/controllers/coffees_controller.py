import flask
from main import db
from main.models import Coffee, User
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity, jwt_optional
)
from typing import Union
app = flask.Blueprint('coffees_controller', __name__)


@app.route("/coffees", methods=['GET'])
@jwt_optional
def get_coffees():
    sql_query = []
    has_review: Union[str, None] = flask.request.args.get(
        'has_review', type=str)
    dripper_id: Union[int, None] = flask.request.args.get(
        'dripper_id', type=int)
    drinker_id: Union[int, None] = flask.request.args.get(
        'drinker_id', type=int)
    bean_id: Union[int, None] = flask.request.args.get('bean_id', type=int)
    current_user: User = User.query.filter_by(
        name=get_jwt_identity()).one_or_none()
    if dripper_id is not None:
        if current_user and dripper_id is current_user.id:
            sql_query.append(Coffee.dripper_id == dripper_id)
        else:
            return flask.jsonify({"result": False, "message": "ログインしてください"}), 401
    if drinker_id is not None:
        if current_user and drinker_id is current_user.id:
            if has_review == "true":
                sql_query.append(Coffee.drinkers.any(id=drinker_id))
                sql_query.append(Coffee.reviews.any(reviewer_id=drinker_id))
            elif has_review == "false":
                sql_query.append(Coffee.drinkers.any(id=drinker_id))
                sql_query.append(~ Coffee.reviews.any(reviewer_id=drinker_id))
        else:
            return flask.jsonify({"result": False, "message": "ログインしてください"}), 401
    if bean_id is not None:
        sql_query.append(Coffee.bean_id == bean_id)
    coffees: list[Coffee] = Coffee.query.filter(
        db.and_(*sql_query)).order_by(db.desc(Coffee.created_at)).limit(50).all()
    return flask.jsonify(
        {
            "result": True,
            "data": [coffee.to_json(with_user=True) for coffee in coffees]
        })


@app.route("/coffees/<int:id>", methods=['GET'])
@jwt_optional
def get_coffee(id: int):
    coffee: Coffee = Coffee.query.get(id)
    return flask.jsonify({
        "result": True,
        "data": coffee.to_json(with_user=get_jwt_identity())
    })


@app.route("/coffees", methods=['POST'])
@jwt_required
def create_coffee():
    form_data = flask.request.json
    current_user: User = User.query.filter_by(
        name=get_jwt_identity()).one_or_none()
    if current_user.id != form_data.get('dripperId'):
        return flask.jsonify({"result": False, "message": "ユーザが不正です"}), 401
    bean_id: int = form_data.get('beanId')
    dripper_id: int = current_user.id
    extraction_time: int = form_data.get('extractionTime')
    extraction_method_id: int = form_data.get('extractionMethodId')
    mesh_id: Union[int, None, str] = form_data.get('meshId')
    memo: str = form_data.get('memo')
    powder_amount: float = form_data.get("powderAmount")
    water_amount: int = form_data.get('waterAmount')
    water_temperature: Union[int, None] = form_data.get('waterTemperature')
    water_temperature = None if water_temperature == "" else water_temperature
    if extraction_time > 10 or extraction_time <= 0 or\
            powder_amount > 20 or powder_amount <= 0 or \
            water_amount <= 0 or water_amount > 500 or\
            water_temperature is not None and\
            (water_temperature > 100 or water_temperature < 0):
        return flask.jsonify({"result": False, "message": "入力が不正です"})
    new_coffee = Coffee(bean_id=bean_id,
                        dripper_id=dripper_id,
                        extraction_time=extraction_time,
                        extraction_method_id=extraction_method_id,
                        mesh_id=mesh_id,
                        memo=memo,
                        powder_amount=powder_amount,
                        water_amount=water_amount,
                        water_temperature=water_temperature)
    db.session.add(new_coffee)
    drinkers = []
    for id in form_data.get('drinkerIds'):
        if id is not None and id != "":
            drinkers.append(int(id))
    drinkers = list(set(drinkers))
    if len(drinkers) == 0:
        return flask.jsonify({"result": False, "message": "飲む人を指定してください"})
    for drinker_id in drinkers:
        drinker = User.query.filter_by(id=drinker_id).one_or_none()
        if not drinker:
            return flask.jsonify({"result": False, "message": "飲む人の指定にあやまりがあります"})
        new_coffee.drinkers.append(drinker)
    db.session.commit()
    return flask.jsonify({
        "result": True,
        "message": "コーヒーを作成しました。",
        "data": new_coffee.to_json(True)
    })
# TODO:ページネーション
