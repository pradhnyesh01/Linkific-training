# Flask SQL API

## Setup

```bash
pip install flask flask-jwt-extended sqlalchemy python-dotenv psycopg2-binary
python3 app.py
```

Create a `.env` file at the project root:

```
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/postgres
```

## Endpoints

### POST /login

Returns a JWT access token.

Body:
```json
{
  "username": "admin",
  "password": "admin"
}
```

All endpoints below require the header:
```
Authorization: Bearer <access_token>
```

---

### POST /students

Adds a new student.

Body:
```json
{
  "name": "Alice",
  "age": 20,
  "course": "CS",
  "marks": 85
}
```

### GET /students

Returns all students.

### PUT /students/<id>

Updates a student by ID. All fields required.

Body:
```json
{
  "name": "Alice",
  "age": 21,
  "course": "CS",
  "marks": 95
}
```

### DELETE /students/<id>

Deletes a student by ID.

## Running SQL Queries

```bash
python3 run_queries.py
```

Executes all statements in `sql_queries.sql` against the database and prints results.

## Tools Used

* Flask
* Flask-JWT-Extended
* SQLAlchemy
* PostgreSQL (Supabase)
* psycopg2
* Postman
