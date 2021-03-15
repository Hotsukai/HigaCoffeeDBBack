from typing import Union, Dict

import flask
from flask_jwt_extended import (get_jwt_identity, jwt_required)

from src.database import db
from src.models.models import Coffee, User, Review, BEANS

app = flask.Blueprint('data_controller', __name__)


@app.route("/data/provide", methods=['GET'])
@jwt_required(optional=True)
def get_provide_count():
    data = {}
    for bean in BEANS:
        bean_data = {"id": bean.id, "fullName": bean.name}
        bean_data["dripCount"] = Coffee.query.filter_by(
            bean_id=bean.id).count()
        bean_data["reviewCount"] = Review.query.filter(
            Review.coffee.has(bean_id=bean.id)).count()
        current_user = User.query.filter_by(
            name=get_jwt_identity()).one_or_none()
        if current_user:
            bean_data["usersDripCount"] = Coffee.query.filter(
                db.and_(
                    Coffee.bean_id == bean.id,
                    Coffee.dripper_id == current_user.id))\
                .count()
            bean_data["usersReviewCount"] = Review.query.filter(
                db.and_(
                    Review.coffee.has(bean_id=bean.id),
                    Review.reviewer_id == current_user.id))\
                .count()
        data[bean.id] = bean_data
    return flask.jsonify({"result": True, "data": data})


@app.route("/data/strongness/<int:bean_id>")
@jwt_required(optional=True)
def get_strongness(bean_id: int):
    strongness_data: Dict[int, Dict[str, float]] = {}
    for strongness in range(1, 5):
        avg: Dict[str, float] = db.session.query(
            db.func.avg(Coffee.extraction_time).label('time'),
            db.func.avg(Coffee.powder_amount).label('powder'),
            db.func.avg(Coffee.water_amount).label('water')).filter(
                db.and_(
                    Coffee.bean_id == bean_id, Review.coffee_id == Coffee.id,
                    strongness - 1 <= Review.strongness,
                    Review.strongness < strongness)).one_or_none()._asdict()
        avg_ex_time: Union[float,
                           None] = float(avg["time"]) if avg["time"] else None
        avg_powder_per_120cc: Union[float, None] = float(avg["powder"])\
            / float(avg["water"])*120 \
            if avg["water"] and avg["powder"] and float(avg["water"]) != 0 \
            else None
        strongness_data[strongness] = {
            "averageExtractionTime": avg_ex_time,
            "averagePowderAmountPer120cc": avg_powder_per_120cc
        }
    current_user: User = User.query.filter_by(
        name=get_jwt_identity()).one_or_none()
    if current_user:
        for strongness in range(1, 5):
            avg: Dict[str, float] = db.session.query(
                db.func.avg(Coffee.extraction_time).label('time'),
                db.func.avg(Coffee.powder_amount).label('powder'),
                db.func.avg(Coffee.water_amount).label('water')).filter(
                    db.and_(Coffee.bean_id == bean_id,
                            Review.coffee_id == Coffee.id,
                            strongness - 1 <= Review.strongness,
                            Review.strongness < strongness, Review.reviewer ==
                            current_user)).one_or_none()._asdict()
            avg_ex_time: Union[float, None] = float(avg["time"]) \
                if avg["time"]\
                else None
            avg_powder_per_120cc: Union[float, None] = float(avg["powder"])\
                / float(avg["water"])*120 \
                if avg["water"] and avg["powder"] and float(avg["water"]) != 0\
                else None
            strongness_data[strongness].update({
                "usersAverageExtractionTime":
                avg_ex_time,
                "usersAveragePowderAmountPer120cc":
                avg_powder_per_120cc
            })
    return flask.jsonify({"result": True, "data": strongness_data})


@app.route("/data/bean_position")
@jwt_required(optional=True)
def get_position():
    position_data: Dict[int, Dict[str, float]] = {}
    for bean in BEANS:
        avg: Dict[str, float] = db.session.query(
            db.func.avg(Review.bitterness).label('bitterness'),
            db.func.avg(Review.strongness).label('strongness'),
            db.func.avg(Review.situation).label('situation'),
            db.func.avg(Review.want_repeat).label('want_repeat')
        ).filter(Coffee.bean_id == bean.id)\
            .filter(Review.coffee_id == Coffee.id)\
            .one_or_none()\
            ._asdict()
        avg_bitterness = float(avg['bitterness'])\
            if avg['bitterness'] else None
        avg_strongness = float(avg['strongness']) \
            if avg['strongness'] else None
        avg_situation = float(avg['situation']) \
            if avg['situation'] else None
        avg_want_repeat = float(avg['want_repeat'])\
            if avg['want_repeat'] else None
        position_data[bean.id] = {
            'avgBitterness': avg_bitterness,
            'avgStrongness': avg_strongness,
            'avgSituation': avg_situation,
            'avgWantRepeat': avg_want_repeat,
            "beanName": BEANS[bean.id - 1].name
        }
    current_user: Union[User, None] = User.query.filter_by(name=get_jwt_identity())\
        .one_or_none()
    if current_user:
        for bean in BEANS:
            avg = db.session.query(
                db.func.avg(Review.bitterness).label('bitterness'),
                db.func.avg(Review.strongness).label('strongness'),
                db.func.avg(Review.situation).label('situation'),
                db.func.avg(Review.want_repeat).label('want_repeat')
            ).filter(Coffee.bean_id == bean.id)\
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
            position_data[bean.id].update({
                'usersAvgBitterness':
                avg_bitterness,
                'usersAvgStrongness':
                avg_strongness,
                'usersAvgSituation':
                avg_situation,
                'usersAvgWantRepeat':
                avg_want_repeat,
            })
    return flask.jsonify({"result": True, "data": position_data})
