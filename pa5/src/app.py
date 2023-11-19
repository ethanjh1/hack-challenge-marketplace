import json
from db import db
from db import Course
from db import User
from db import Assignment
from flask import Flask
from flask import request

app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


def success_response(data, code=200):
   return json.dumps(data), code


def failure_response(data, code=404):
   return json.dumps({"error": data}), code


# your routes here

@app.route("/")
def greeting():
   return f"hello"

@app.route("/api/courses/", methods = ["GET"])
def get_courses():
    """
    Endpoint for getting all courses
    """
    courses = []

    for course in Course.query.all():
      courses.append(course.serialize())

    return success_response({"courses": courses}, 200)


@app.route("/api/courses/", methods = ["POST"])
def add_course():
    """
    Endpoint for adding a course
    """
    body = json.loads(request.data)
    code = body.get("code")
    name = body.get("name")
    if code is None or name is None:
        return failure_response("Input not found!", 400)
    new_course = Course(code = body.get("code"), name = body.get("name"))
    db.session.add(new_course)
    db.session.commit()

    return success_response(new_course.serialize(), 201)


@app.route("/api/courses/<int:course_id>/", methods = ["GET"])
def get_course(course_id):
  """
  Endpoint for getting a specific course
  """
  course = Course.query.filter_by(id = course_id).first()
  if course is None:
     return failure_response("Course not found!", 404)
  return success_response(course.serialize(), 200)


@app.route("/api/courses/<int:course_id>/", methods = ["DELETE"])
def delete_course(course_id):
  """
  Endpoint for deleting a specific course
  """
  course = Course.query.filter_by(id = course_id).first()
  if course is None:
     return failure_response("Course not found!", 404)
  db.session.delete(course)
  db.session.commit()
  return success_response(course.serialize(), 200)


@app.route("/api/users/", methods = ["POST"])
def create_user():
  """
  Endpoint for creating a user
  """
  body = json.loads(request.data)
  name = body.get("name")
  netid = body.get("netid")
  if name is None or netid is None:
      return failure_response("Input not found!", 400)
  new_user = User(name = body.get("name"), netid = body.get("netid"))
  db.session.add(new_user)
  db.session.commit()
  return success_response(new_user.serialize(), 201)


@app.route("/api/users/<int:user_id>/", methods = ["GET"])
def get_user(user_id):
  """
  Endpoint for getting a specific user
  """
  user = User.query.filter_by(id = user_id).first()
  if user is None:
    return failure_response("Input not found!", 404)
  return json.dumps(user.serialize()), 200


@app.route("/api/courses/<int:course_id>/add/", methods = ["POST"])
def add_user_to_course(course_id):
  """
  Endpoint for adding a user to a course
  """
  body = json.loads(request.data)
  user = User.query.filter_by(id = body.get("user_id")).first()
  type = body.get("type")
  course = Course.query.filter_by(id = course_id).first()

  if body.get("user_id") is None or type is None or user is None:
     return json.dumps("Input not found"), 404
  if course is None:
     return json.dumps("Input not found"), 404
  if type == "instructor":
    course.instructors.append(user)
  if type == "student":
    course.students.append(user)
  db.session.commit()
  return json.dumps(course.serialize()), 200
  

@app.route("/api/courses/<int:course_id>/assignment/", methods = ["POST"])
def create_assignment_for_course(course_id):
  """
  Endpoint for creating an assignment for a course
  """
  body = json.loads(request.data)
  course = Course.query.filter_by(id = course_id).first()
  if body.get("title") is None or body.get("due_date") is None:
     return failure_response("Input not found!", 400)
  if course is None:
     return failure_response("Course not found!", 404)
  new_assignment = Assignment(title = body.get("title"), due_date = body.get("due_date"))
  new_assignment.courses.append(course)
  db.session.add(new_assignment)
  db.session.commit()
  return json.dumps(new_assignment.serialize()), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
