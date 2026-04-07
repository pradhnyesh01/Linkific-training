from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Student
from config import DB_URI, JWT_SECRET_KEY
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY

jwt = JWTManager(app)

# DB setup
engine = create_engine(DB_URI, connect_args={"sslmode": "require"})
Session = scoped_session(sessionmaker(bind=engine))
session = Session()

Base.metadata.create_all(engine)

# ---------------- AUTH ----------------
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    if username == "admin" and password == "admin":
        token = create_access_token(identity=username)
        return jsonify(access_token=token)

    return jsonify({"msg": "Invalid credentials"}), 401


# ---------------- CREATE ----------------
@app.route("/students", methods=["POST"])
@jwt_required()
def add_student():
    data = request.json

    student = Student(
        name=data["name"],
        age=data["age"],
        course=data["course"],
        marks=data["marks"]
    )

    session.add(student)
    session.commit()

    return jsonify({"msg": "Student added"})


# ---------------- READ ----------------
@app.route("/students", methods=["GET"])
@jwt_required()
def get_students():
    students = session.query(Student).all()

    result = []
    for s in students:
        result.append({
            "id": s.id,
            "name": s.name,
            "age": s.age,
            "course": s.course,
            "marks": s.marks
        })

    return jsonify(result)


# ---------------- UPDATE ----------------
@app.route("/students/<int:id>", methods=["PUT"])
@jwt_required()
def update_student(id):
    data = request.json
    student = session.query(Student).filter_by(id=id).first()

    if not student:
        return jsonify({"msg": "Not found"}), 404

    student.name = data["name"]
    student.age = data["age"]
    student.course = data["course"]
    student.marks = data["marks"]

    session.commit()

    return jsonify({"msg": "Updated"})


# ---------------- DELETE ----------------
@app.route("/students/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_student(id):
    student = session.query(Student).filter_by(id=id).first()

    if not student:
        return jsonify({"msg": "Not found"}), 404

    session.delete(student)
    session.commit()

    return jsonify({"msg": "Deleted"})


if __name__ == "__main__":
    app.run(debug=True)