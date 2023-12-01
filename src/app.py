import json
from db import db
from db import User
from db import Good
from db import Transaction
from db import Rating
from flask import Flask
from flask import request
import os

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


@app.route("/api/reset/", methods=["POST"])
def reset_database():
   db.drop_all()
   db.create_all()
   return success_response({"message": "Database reset successfully"})

# -- USER ROUTES -----------------------------------------------------------------------------------


@app.route("/api/users/", methods=["POST"])
def create_user():
   """
   Endpoint for creating a user
   """
   body = json.loads(request.data)
   if "name" not in body or "netid" not in body:
      return failure_response("Incomplete user information", 400)
   new_user = User(
      name=body.get("name"),
      netid=body.get("netid")
   )
   existing_user = User.query.filter_by(netid=body.get("netid")).first()
   if existing_user:
      return failure_response("User already exists", 400)
   db.session.add(new_user)
   db.session.commit()
   return success_response(new_user.serialize(), 201)


@app.route("/api/users/<int:user_id>/", methods=["GET"])
def get_user(user_id):
   """
   Endpoint for getting a specific user
   """
   user = User.query.filter_by(id=user_id).first()
   if user is None:
      return failure_response("User not found!", 404)
   return success_response(user.public_serialize(), 200)


@app.route("/api/users/<int:user_id>/transactions/", methods=["GET"])
def get_transaction_by_user(user_id):
   """
   Endpoint for getting the transaction history of a specific user
   """
   user = User.query.filter_by(id=user_id).first()
   if user is None:
      return failure_response("User not found!", 404)
   return success_response(user.serialize()["transactions"], 200)


@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
   """
   Endpoint for deleting a specific user
   """
   user = User.query.filter_by(id=user_id).first()
   if user is None:
      return failure_response("User not found!", 404)
   db.session.delete(user)
   db.session.commit()
   return success_response(user.serialize(), 200)


@app.route("/api/users/<int:user_id>/", methods=["PATCH"])
def update_user(user_id):
   """
   Endpoint for updating a user's name
   """
   body = json.loads(request.data)
   user = User.query.filter_by(id=user_id).first()
   if user is None:
      return failure_response("User not found!", 404)
   if "name" not in body:
      return failure_response("Incomplete user information", 400)
   user.name = body.get("name")
   db.session.commit()
   return success_response(user.serialize(), 201)

# -- GOOD ROUTES -----------------------------------------------------------------------------------

@app.route("/api/goods/", methods=["POST"])
def create_good():
   """
   Endpoint for creating a good
   """
   body = json.loads(request.data)
   if not ("good_name" in body and "image" in body and "price" in body and "seller_id" in body):
      return failure_response("Incomplete good information", 400)
   new_good = Good(
      good_name=body.get("good_name"),
      image_url=body.get("image"),
      price=body.get("price"),
      seller_id=body.get("seller_id")
   )
   existing_user = User.query.filter_by(netid=body.get("netid")).first()
   if existing_user:
      return failure_response("Good already exists", 400)
   db.session.add(new_good)
   db.session.commit()
   return success_response(new_good.serialize(), 201)


@app.route("/api/goods/<int:good_id>/", methods=["GET"])
def get_good(good_id):
   """
   Endpoint for getting a specific good
   """
   good = Good.query.filter_by(id=good_id).first()
   if good is None:
      return failure_response("Good not found!", 404)
   return success_response(good.public_serialize(), 200)


@app.route("/api/goods/", methods=["GET"])
def get_goods():
    """
    Endpoint for getting all goods
    """
    goods = []

    for good in Good.query.all():
        goods.append(good.serialize())

    return success_response({"Goods": goods}, 200)


@app.route("/api/goods/<int:good_id>/", methods=["DELETE"])
def delete_good(good_id):
    """
    Endpoint for deleting a specific good
    """
    good = Good.query.filter_by(id=good_id).first()
    if good is None:
        return failure_response("Good not found!", 404)
    db.session.delete(good)
    db.session.commit()
    return success_response(good.serialize(), 200)


@app.route("/api/goods/<int:good_id>/", methods=["PATCH"])
def update_good(good_id):
    """
    Endpoint for updating a good
    """
    body = json.loads(request.data)
    good = Good.query.filter_by(id=good_id).first()
    if good is None:
        return failure_response("Good not found!", 404)
    if "good_name" not in body and "price" not in body:
        return failure_response("Incomplete user information", 400)
    if "good_name" in body:
        good.good_name = body.get("good_name")
    if "price" in body:
        good.price = body.get("price")
    db.session.commit()
    return success_response(good.serialize(), 201)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
