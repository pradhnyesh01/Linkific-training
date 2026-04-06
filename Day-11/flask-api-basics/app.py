from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Sample data
items = [
    {"id": 1, "name": "Day-11 Task"},
    {"id": 2, "name": "Postman testing..."}
]

# 1. Hello World
@app.route('/')
def home():
    return "Hello, Flask!"

# 2. GET all items
@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(items)

# 3. GET item by ID
@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    for item in items:
        if item["id"] == item_id:
            return jsonify(item)
    return jsonify({"error": "Item not found"}), 404

# 4. POST new item
@app.route('/items', methods=['POST'])
def add_item():
    data = request.json
    new_item = {
        "id": len(items) + 1,
        "name": data.get("name")
    }
    items.append(new_item)
    return jsonify(new_item), 201

# 5. PUT update item
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    for item in items:
        if item["id"] == item_id:
            item["name"] = data.get("name", item["name"])
            return jsonify(item)
    return jsonify({"error": "Item not found"}), 404

# 6. DELETE item
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    for item in items:
        if item["id"] == item_id:
            items.remove(item)
            return jsonify({"message": "Item deleted"})
    return jsonify({"error": "Item not found"}), 404

@app.route('/items/<int:item_id>', methods=['PATCH'])
def patch_item(item_id):
    data = request.json
    for item in items:
        if item["id"] == item_id:
            if "name" in data:
                item["name"] = data["name"]
            return jsonify(item)
    return jsonify({"error": "Item not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)