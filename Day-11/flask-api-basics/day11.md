# Flask API Basics

## Setup

```bash
pip install flask flask-cors
python app.py
```

## Endpoints

### GET /items

Returns all items

### GET /items/<id>

Returns a specific item

### POST /items

Creates a new item
Body:

```json
{
  "name": "Item Name"
}
```

### PUT /items/<id>

Updates an item, where all the fields need to be filled

### DELETE /items/<id>

Deletes an item

### PATCH /items/<id>

Updates an item, where only field changed needs to be filled

## Tools Used

* Flask
* Postman
