from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table_instructors = db.Table(
    "assocation_instructors",
    db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("course.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
 
)

association_table_students = db.Table(
    "assocation_students",
    db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("course.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),

)
association_table_assignments = db.Table(
    "assocation_assignments",
    db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("course.id")),
    db.Column("assignment_id", db.Integer, db.ForeignKey("assignment.id"))

)
   

# your classes here
class Course(db.Model):
  """
    Database driver for the Venmo (Full) app.
    Handles with reading and writing data with the database.
  """
  __tablename__ = 'course'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  code = db.Column(db.String, nullable=False)
  name = db.Column(db.String, nullable=False)
  assignments = db.relationship('Assignment', secondary = association_table_assignments, back_populates = 'courses')
  instructors = db.relationship('User', secondary = association_table_instructors, back_populates = 'courses_instructor')
  students = db.relationship('User', secondary = association_table_students, back_populates = 'courses_student')

  def __init__(self, **kwargs):
    self.code = kwargs.get("code")
    self.name = kwargs.get("name")

  def serialize(self):
    return {
        "id": self.id,
        "code": self.code,
        "name": self.name,
        "assignments": [assignment.simple_serialize() for assignment in self.assignments],
        "instructors": [instructor.simple_serialize() for instructor in self.instructors],
        "students": [student.simple_serialize() for student in self.students]
    }

  def simple_serialize(self):
    return {"id": self.id, "code": self.code, "name": self.name}


class User(db.Model):
  """
    Database driver for the Venmo (Full) app.
    Handles with reading and writing data with the database.
  """
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String, nullable=False)
  netid = db.Column(db.String, nullable=False)
  courses_instructor = db.relationship('Course', secondary = association_table_instructors, back_populates = 'instructors')
  courses_student = db.relationship('Course', secondary = association_table_students, back_populates = 'students')

  def __init__(self, **kwargs):
    self.name = kwargs.get("name")
    self.netid = kwargs.get("netid")

  def serialize(self):
    return {
        "id": self.id,
        "name": self.name,
        "netid": self.netid,
        "courses": [course.simple_serialize() for course in self.courses_instructor] + [course.simple_serialize() for course in self.courses_student]
    }

  def simple_serialize(self):
    return {"id": self.id, "name": self.name, "netid": self.netid}


class Assignment(db.Model):
  """
    Database driver for the Venmo (Full) app.
    Handles with reading and writing data with the database.
  """
  __tablename__ = 'assignment'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  title = db.Column(db.String, nullable=False)
  due_date = db.Column(db.Integer, nullable=False)
  courses = db.relationship('Course', secondary = association_table_assignments, back_populates = 'assignments')

  def __init__(self, **kwargs):
    self.title = kwargs.get("title")
    self.due_date = int(kwargs.get("due_date"))

  def serialize(self):
    return {
      "id": self.id, 
      "title": self.title, 
      "due_date": int(self.due_date), 
      "course": self.courses[0].simple_serialize()
      }
  
  def simple_serialize(self):
    return {"id": self.id, "title": self.title, "due_date": int(self.due_date)}