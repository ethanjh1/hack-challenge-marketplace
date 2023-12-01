import json
from db import db
from db import User
from db import Good
from db import Transaction
# from db import Rating
from flask import Flask
from flask import request

import base64
import boto3
import datetime
import io
from io import BytesIO
from mimetypes import guess_extension, guess_type
import os
from PIL import Image
import random
import re
import string
import requests

app = Flask(__name__)
db_filename = "marketplace.db"

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

EXTENSIONS = ["png", "gif", "jpg", "jpeg"]
BASE_DIR = os.getcwd()
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.us-east-1.amazonaws.com"


# -- HELPER FUNCTIONS ------------------------------------------------------------------------------

def success_response(data, code=200):
    """
    Returns a JSON serialized success response with a status code
    """
    return json.dumps(data), code


def failure_response(data, code=404):
    """
    Returns a JSON serialized failure response with a status code
    """
    return json.dumps({"error": data}), code


def create(image_data):
    """
    Given an image in base64 encoding, does the following:
    1. Rejects the image if it is not a supported filetype
    2. Generate a random string for the image filename
    3. Decodes the image and attempts to upload to AWS S3
    """
    try:
        ext = guess_extension(guess_type(image_data)[0])[1:]
        if ext not in EXTENSIONS:
            raise Exception(f"Extension {ext} is not valid")
        salt = "".join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.digits
            )
            for _ in range(16)
        )
        img_str = re.sub(r"^data:image\/[^;]+;base64,", "", image_data)
        img_data = base64.b64decode(img_str)
        img = Image.open(BytesIO(img_data))
        img_filename = f"{salt}.{ext}"
        return upload(img, img_filename)
    except Exception as e:
        return f"Error when creating image: {e}", False


def upload(img, img_filename):
    """
    Attempts to upload image to the specified bucket
    """
    try:
        # temporarily save on server
        img_temp_loc = f"{BASE_DIR}/{img_filename}"
        img.save(img_temp_loc)
        print("temp saved")

        # upload image to S3
        s3_client = boto3.client("s3")
        # print(S3_BUCKET_NAME)
        print(os.environ)
        s3_client.upload_file(img_temp_loc, S3_BUCKET_NAME, img_filename)
        print("uploaded")

        # make S3 image url public
        s3_resource = boto3.resource("s3")
        object_acl = s3_resource.ObjectAcl(S3_BUCKET_NAME, img_filename)
        object_acl.put(ACL="public-read")
        print("public")

        # remove from temporary save location
        os.remove(img_temp_loc)
        return f"{S3_BASE_URL}/{img_filename}", True
    except Exception as e:
        return f"Error when uploading image: {e}", False


def b64_encode(good_serialized):
    """
    Replaces the image URL in a serialized Good with a corresponding encoded base64 string
    """
    image_url = good_serialized.get('image_url')
    encoded = {
        'id': good_serialized.get('id'),
        'good_name': good_serialized.get('good_name'),
        'image': base64.b64encode(requests.get(image_url).content).decode('utf-8'),
        'price': good_serialized.get('price')
    }
    if good_serialized.get('seller') is not None:
        encoded['seller'] = good_serialized.get('seller')
    return encoded


# -- TESTING ROUTES --------------------------------------------------------------------------------

@app.route("/api/reset/", methods=["POST"])
def reset_database():
    """
    Endpoint for resetting the database by dropping and recreating all tables
    """
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
    Endpoint for getting a specific user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found", 404)
    return success_response(user.simple_serialize(), 200)


@app.route("/api/users/<int:user_id>/goods/", methods=["GET"])
def get_goods_by_user(user_id):
    """
    Endpoint for getting the posted goods of a specific user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found", 404)
    return success_response({"goods": user.simple_serialize()["goods"]}, 200)


@app.route("/api/users/<int:user_id>/transactions/", methods=["GET"])
def get_transactions_by_user(user_id):
    """
    Endpoint for getting the transaction history of a specific user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found", 404)
    return success_response({"transactions": user.serialize()["transactions"]}, 200)


@app.route("/api/users/<int:user_id>/rating/", methods=["GET"])
def get_rating_by_user(user_id):
    """
    Endpoint for getting the rating of a specific user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found", 404)
    return success_response({"rating": user.serialize()["rating"]}, 200)


@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Endpoint for deleting a specific user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found", 404)
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
        return failure_response("User not found", 404)
    if "name" not in body:
        return failure_response("Incomplete user information", 400)
    user.name = body.get("name")
    db.session.commit()
    return success_response(user.serialize(), 200)


# -- GOOD ROUTES -----------------------------------------------------------------------------------

@app.route("/api/goods/", methods=["POST"])
def create_good():
    """
    Endpoint for creating a good
    """
    body = json.loads(request.data)
    if not ("good_name" in body and "image" in body and "price" in body and "seller_id" in body):
        return failure_response("Incomplete good information", 400)
    seller = User.query.filter_by(id=body.get("seller_id")).first()
    if seller is None:
        return failure_response("Seller not found", 404)
    image_url, status = create(body.get("image"))
    if not status:
        return failure_response(image_url, 400)
    new_good = Good(
        good_name=body.get("good_name"),
        image_url=image_url,
        price=body.get("price"),
        seller_id=body.get("seller_id")
    )
    db.session.add(new_good)
    db.session.commit()
    return success_response(b64_encode(new_good.serialize()), 201)


@app.route("/api/goods/<int:good_id>/", methods=["GET"])
def get_good(good_id):
    """
    Endpoint for getting a specific good
    """
    good = Good.query.filter_by(id=good_id).first()
    if good is None:
        return failure_response("Good not found", 404)
    return success_response(b64_encode(good.serialize()), 200)


@app.route("/api/goods/", methods=["GET"])
def get_goods():
    """
    Endpoint for getting all goods
    """
    goods = [b64_encode(g.serialize()) for g in Good.query.all()]
    return success_response({"goods": goods}, 200)


@app.route("/api/goods/<int:good_id>/", methods=["DELETE"])
def delete_good(good_id):
    """
    Endpoint for deleting a specific good
    """
    good = Good.query.filter_by(id=good_id).first()
    if good is None:
        return failure_response("Good not found", 404)
    db.session.delete(good)
    db.session.commit()
    return success_response(b64_encode(good.serialize()), 200)


@app.route("/api/goods/<int:good_id>/", methods=["PATCH"])
def update_good(good_id):
    """
    Endpoint for updating a good's name or price
    """
    body = json.loads(request.data)
    good = Good.query.filter_by(id=good_id).first()
    if good is None:
        return failure_response("Good not found", 404)
    if "good_name" not in body and "price" not in body:
        return failure_response("Incomplete user information", 400)
    if "good_name" in body:
        good.good_name = body.get("good_name")
    if "price" in body:
        good.price = body.get("price")
    db.session.commit()
    return success_response(b64_encode(good.serialize()), 200)


# -- TRANSACTION ROUTES -------------------------------------------------------------------------------

@app.route("/api/transactions/", methods=["POST"])
def create_transaction():
    """
    Endpoint for creating a transaction
    """
    # make sure only one transaction per good_id
    body = json.loads(request.data)
    if not ("amount" in body and "good_id" in body and "seller_id" in body and "buyer_id" in body):
        return failure_response("Incomplete transaction information", 400)
    good = Good.query.filter_by(id=body.get("good_id")).first()
    if good is None:
        return failure_response("Good not found", 404)
    buyer = User.query.filter_by(id=body.get("buyer_id")).first()
    if buyer is None:
        return failure_response("Buyer not found", 404)
    seller = User.query.filter_by(id=body.get("seller_id")).first()
    if seller is None:
        return failure_response("Seller not found", 404)
    new_transaction = Transaction(
        amount=body.get("amount"),
        good_id=body.get("good_id"),
        rating=body.get("rating")
    )
    new_transaction.buyer.append(buyer)
    new_transaction.seller.append(seller)
    db.session.add(new_transaction)
    db.session.commit()
    return success_response(new_transaction.serialize(), 201)


@app.route("/api/transactions/<int:transaction_id>/", methods=["PATCH"])
def update_rating(transaction_id):
    """
    Endpoint for updating a rating
    """
    body = json.loads(request.data)
    transaction = Transaction.query.filter_by(id=transaction_id).first()
    if transaction is None:
        return failure_response("Good not found", 404)
    if "rating" not in body:
        return failure_response("No rating value given", 400)
    transaction.rating = body.get("rating")
    db.session.commit()
    return success_response(transaction.serialize(), 200)


# # -- RATING ROUTES -------------------------------------------------------------------------------

# @app.route("/api/rating/<int:transaction_id>/", methods=["POST"])
# def create_rating(transaction_id):
#     """
#     Endpoint for creating a rating
#     """
#     body = json.loads(request.data)
#     if not ("value" in body):
#         return failure_response("Incomplete rating information", 400)
#     transaction = Transaction.query.filter_by(id=transaction_id).first()
#     if transaction is None:
#         return failure_response("Transaction not found", 404)
#     new_rating = Rating(
#         value=body.get("value"),
#         transaction_id = transaction_id
#     )
#     db.session.add(new_rating)
#     db.session.commit()
#     return success_response(new_rating.serialize(), 201)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
