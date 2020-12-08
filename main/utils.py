from main.models import Coffee, BEAN
from flask.json import jsonify


def convert_coffees_to_json(coffees):
    json = []
    for coffee in coffees:
        json.append(convert_coffee_to_json(coffee))
    return json


def convert_coffee_to_json(coffee):
    return{
        "powderAmount": coffee.powder_amount,
        "id": coffee.id,
        "extractionTime": coffee.extraction_time,
        "extractionMethodId": coffee.extraction_method_id,
        "meshId": coffee.mesh_id,
        # TODO: mesh,method,dripperのname
        "waterAmount": coffee.water_amount,
        "waterTemperature": coffee.water_temperature,
        "beanId": coffee.bean_id,
        "bean": BEAN[coffee.bean_id],
        "memo": coffee.memo,
        "dripperId": coffee.dripper.id,
        "createdAt": coffee.created_at
    }


def convert_user_to_json(user):
    return {"id": user.id,
            "name": user.name,
            "profile": user.profile,
            "created_at": user.created_at,
            "updated_at": user.updated_at}


def convert_review_to_json(review):
    return {
        "id": review.id,
        "bitterness": review.bitterness,
        "coffeeId": review.coffee_id,
        "feeling": review.feeling,
        "reviewerId": review.reviewer_id,
        "situation": review.situation,
        "strongness": review.strongness,
        "wantRepeat": review.want_repeat,
        "createdAt": review.created_at,
        "updatedAt": review.updated_at,
    }


def convert_reviews_to_json(reviews):
    json = []
    for review in reviews:
        json.append(convert_review_to_json(review))
    return json
