from main.models import Coffee, BEAN, MESH, EXTRACTION_METHOD
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
        "extractionMethod": EXTRACTION_METHOD[coffee.extraction_method_id] if coffee.extraction_method_id else None,
        "mesh": MESH[coffee.mesh_id] if coffee.mesh_id else None,
        "waterAmount": coffee.water_amount,
        "waterTemperature": coffee.water_temperature,
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
        "coffee": convert_coffee_to_json(review.coffees),
        "feeling": review.feeling,
        "reviewer": convert_user_to_json(review.users),
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
