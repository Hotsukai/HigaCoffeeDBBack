from flask.json import jsonify


def convert_entries_to_json(entries):
    json = {"data": []}
    for entry in entries:
        json["data"].append({"title": entry.title, "text": entry.text})
    return jsonify(json)
