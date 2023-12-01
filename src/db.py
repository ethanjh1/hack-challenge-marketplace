from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

buyers_table = db.Table('buyers',
                        db.Column('user_id', db.Integer,
                                  db.ForeignKey('user.id')),
                        db.Column('transaction_id', db.Integer,
                                  db.ForeignKey('transaction.id'))
                        )
sellers_table = db.Table('sellers',
                         db.Column('user_id', db.Integer,
                                   db.ForeignKey('user.id')),
                         db.Column('transaction_id', db.Integer,
                                   db.ForeignKey('transaction.id'))
                         )


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    netid = db.Column(db.String(128), unique=True, nullable=False)
    rating = db.Column(db.Float, default=5.0)
    goods = db.relationship("Good", cascade="delete")
    buyer_transactions = db.relationship(
        'Transaction', secondary=buyers_table, back_populates='buyer')
    seller_transactions = db.relationship(
        'Transaction', secondary=sellers_table, back_populates='seller')

    def __init__(self, **kwargs):
        """
        Initialize a User object
        """
        self.name = kwargs.get("name", "")
        self.netid = kwargs.get("netid", "")
        self.rating = 5.0

    def serialize(self):
        """
        Serialize a User object
        """
        count = 1
        sum = self.rating
        for t in self.seller_transactions:
            if t.serialize()['rating'] is not None:
                count += 1
                sum += t.serialize()['rating']
        return {
            'id': self.id,
            'name': self.name,
            'netid': self.netid,
            'rating': sum / count,
            'goods': [g.simple_serialize() for g in self.goods],
            'transactions': [t.serialize() for t in self.buyer_transactions] + [t.serialize() for t in self.seller_transactions]
        }

    def simple_serialize(self):
        """
        Serialize a User object without transactions
        """
        return {
            'id': self.id,
            'name': self.name,
            'netid': self.netid,
            'rating': self.rating,
            'goods': [g.simple_serialize() for g in self.goods]
        }
    
    def simpler_serialize(self):
        """
        Serialize a User object without transactions and goods
        """
        return {
            'id': self.id,
            'name': self.name,
            'netid': self.netid,
            'rating': self.rating
        }

class Good(db.Model):
    __tablename__ = 'good'
    id = db.Column(db.Integer, primary_key=True)
    good_name = db.Column(db.String(128), nullable=False)
    image_url = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Integer, nullable=False)  # cents
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, **kwargs):
        """
        Initialize a Good object
        """
        self.good_name = kwargs.get("good_name", "")
        self.image_url = kwargs.get("image_url", "")
        self.price = kwargs.get("price", 0)
        self.seller_id = kwargs.get("seller_id", 0)

    def serialize(self):
        """
        Serialize a Good object
        """
        return {
            'id': self.id,
            'good_name': self.good_name,
            'image_url': self.image_url,
            'price': self.price,
            'seller': User.query.filter_by(id=self.seller_id).first().simpler_serialize()
        }

    def simple_serialize(self):
        """
        Serialize a Good object without seller
        """
        return {
            'id': self.id,
            'good_name': self.good_name,
            'image_url': self.image_url,
            'price': self.price
        }


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    good_id = db.Column(db.Integer, db.ForeignKey('good.id'))
    amount = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False,
                          default=db.func.current_timestamp())
    buyer = db.relationship('User', secondary=buyers_table,
                            back_populates='buyer_transactions')
    seller = db.relationship(
        'User', secondary=sellers_table, back_populates='seller_transactions')

    def __init__(self, **kwargs):
        """
        Initialize a Transaction object
        """
        self.buyer_id = kwargs.get("buyer_id")
        self.seller_id = kwargs.get("seller_id")
        self.good_id = kwargs.get("good_id")
        self.amount = kwargs.get("amount", 0)
        self.timestamp = kwargs.get("timestamp", db.func.current_timestamp())
        self.rating = kwargs.get("rating")
        

    def serialize(self):
        """
        Serialize a Transaction object
        """
        return {
            'id': self.id,
            'good': Good.query.filter_by(id=self.good_id).first().simple_serialize(),
            'buyer': [buyer.simpler_serialize() for buyer in self.buyer],
            'seller': [seller.simpler_serialize() for seller in self.seller],
            'amount': self.amount,
            'timestamp': self.timestamp.isoformat(),
            'rating': self.rating
        }


# class Rating(db.Model):
#     __tablename__ = 'rating'
#     id = db.Column(db.Integer, primary_key=True)
#     value = db.Column(db.Integer, nullable=False)
#     transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'))

#     def __init__(self, **kwargs):
#         """
#         Initialize a Rating object
#         """
#         self.value = kwargs.get("value", 0)
#         self.transaction_id = kwargs.get("transaction_id")

#     def serialize(self):
#         return {
#             'id': self.id,
#             'value': self.value,
#             'transaction': Transaction.query.filter_by(id=self.transaction_id).first().serialize()
#         }
