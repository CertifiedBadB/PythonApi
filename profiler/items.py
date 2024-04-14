from flask import Blueprint, jsonify, request

from .db import get_db

blueprint = Blueprint("items", __name__, url_prefix="/items")

# post a new item
@blueprint.route("/", methods=["POST"])
def create_item():
    data = request.json

    name = data.get("name") 
    description = data.get("description") 
    uri = data.get("uri") 

    if not all([name, description, uri]):
        return {"error": "Required fields are missing"}, 400
    
    if not isinstance(name, str) or not isinstance(description, str) or not isinstance(uri, str):
        return {"error": "Invalid data types for fields"}, 400

    db = get_db()

    try:
        cursor = db.execute(
            "INSERT INTO item (name, description, uri) VALUES (?, ?, ?)",
            (name, description, uri),
        )
        db.commit()
    except db.Error:
        return {"error": "The database call couldnt be made"}, 500
        

    return jsonify({"id": cursor.lastrowid,
                    "name":name,
                    "description": description,
                    "uri":uri}), 201

# get a list off all items
@blueprint.route("/", methods=["GET"])
def list_items():
    db = get_db()

    try:
        cursor = db.execute("SELECT * FROM item")
        items = cursor.fetchall()

        item_list = []
        for item in items:
            item_list.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "description": item["description"],
                    "uri": item["uri"],
                    "created": item["created"]
                }
            )

        return jsonify(item_list)
    except db.Error:
        return {"error": "The database call couldnt be made"}, 500 


# get 1 item using the id
@blueprint.route("/<int:item_id>/", methods=["GET"])
def get_item(item_id):
    db = get_db()
    
    try:
        cursor = db.execute("SELECT * FROM item WHERE id=?", (item_id,))
        item = cursor.fetchone()

        if item is None:
            return {"error": "Ivalid item."}, 400 

        return {
            "id": item["id"],
            "name": item["name"],
            "description": item["description"],
            "uri": item["uri"],
            "created": item["created"]
        }
    except db.Error:
        return {"error": "The database call couldnt be made"}, 500 


# edit 1 item using the id
@blueprint.route("/<int:item_id>/", methods=["PUT"])
def update_item(item_id):
    data = request.json

    already_created = get_item(item_id)

    name = data.get("name") or already_created.get("name")
    description = data.get("description") or already_created.get("description")
    uri = data.get("uri") or already_created.get("uri")

    if not isinstance(name, str) or not isinstance(description, str) or not isinstance(uri, str):
        return {"error": "Invalid data types for fields"}, 400

    db = get_db()

    try:
        db.execute(
            "UPDATE item SET name=?, description=?, uri=? WHERE id=?",
            (name, description, uri, item_id),
        )
        db.commit()
    except db.Error:
        return {"error": "The database call couldnt be made"}, 500 

    return jsonify({
        "id": item_id,
        "name":name,
        "description":description,
        "uri":uri,
        "created":already_created.get("created")
        }), 200

# delete 1 item using the id
@blueprint.route("/<int:item_id>/", methods=["DELETE"])
def delete_item(item_id):
    db = get_db()
    try:
        db.execute("DELETE FROM item WHERE id=?", (item_id,))
        db.commit()
    except db.Error:
        return {"error": "The database call couldn't be made"}, 500
    
    return jsonify({"id": item_id,
                    "deleted": True}), 201
    