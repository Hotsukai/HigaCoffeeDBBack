from flask.json import jsonify


def convert_entries_to_json(entries):
    json = {"data": []}
    for entry in entries:
        json["data"].append({"title": entry.title, "text": entry.text})
    return json


def convert_coffees_to_json(coffees):
    json = {"data": []}
    for coffee in coffees:
        json["data"].append({
            "powder_amount": coffee.powder_amount,
            "extraction_time": coffee.extraction_time,
            "extraction_method_id": coffee.extraction_method_id,
            "mesh_id": coffee.mesh_id,
            "water_amount": coffee.water_amount,
            "water_temperature": coffee.water_temperature,
            "bean_id": coffee.bean_id,
            "dripper_id": coffee.dripper.id,
            "drinker_id": coffee.drinker_id,
        })
    return json


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
        "reviewerId":review.reviewer_id,
        "situation": review.situation,
        "strongness": review.strongness,
        "wantRepeat": review.want_repeat,
        "createdAt": review.created_at,
        "updatedAt": review.updated_at
    }


def convert_reviews_to_json(reviews):
    json = {"data": []}
    for review in reviews:
        json["data"].append({
            "id": review.id,
            "bitterness": review.bitterness,
            "wantRepeat": review.want_repeat,
            "situation": review.situation,
            "strongness": review.strongness,
            "feeling": review.feeling,
            "created_at": review.created_at,
            "updated_at": review.updated_at
        })
    return json
