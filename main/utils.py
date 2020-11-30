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
