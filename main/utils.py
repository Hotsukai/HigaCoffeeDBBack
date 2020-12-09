from main.models import Coffee, BEAN, MESH, EXTRACTION_METHOD
from flask.json import jsonify


def convert_coffees_to_json(coffees, with_user=False):
    json = []
    for coffee in coffees:
        json.append(convert_coffee_to_json(coffee, with_user))
    return json


def convert_coffee_to_json(coffee, with_user: False):
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
        "dripper": convert_user_to_json(coffee.dripper) if with_user else None,
        "createdAt": coffee.created_at
    }


def convert_user_to_json(user):
    return {"id": user.id,
            "name": user.name,
            "profile": user.profile,
            "created_at": user.created_at,
            "updated_at": user.updated_at}


def convert_review_to_json(review, with_user=False):
    return {
        "id": review.id,
        "bitterness": review.bitterness,
        "coffee": convert_coffee_to_json(review.coffees, with_user=with_user),
        "feeling": review.feeling,
        "reviewer": convert_user_to_json(review.users) if with_user else None,
        "situation": review.situation,
        "strongness": review.strongness,
        "wantRepeat": review.want_repeat,
        "createdAt": review.created_at,
        "updatedAt": review.updated_at,
    }


def convert_reviews_to_json(reviews, with_user=False):
    json = []
    for review in reviews:
        json.append(convert_review_to_json(review, with_user))
    return json
