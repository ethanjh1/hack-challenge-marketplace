from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Many-to-many relationship between Users and Goods
users_goods_table = db.Table('users_goods',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('good_id', db.Integer, db.ForeignKey('good.id'))
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    netid = db.Column(db.String(128), unique=True, nullable=False)
    rating = db.Column(db.Float, default=0.0)
    goods = db.relationship('Good', secondary=users_goods_table, back_populates='owners')
    transactions = db.relationship('Transaction', back_populates='user')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'netid': self.netid,
            'rating': self.rating,
            'goods': [good.serialize_without_user() for good in self.goods],
            'transactions': [transaction.serialize() for transaction in self.transactions]
        }

class Good(db.Model):
    __tablename__ = 'good'
    id = db.Column(db.Integer, primary_key=True)
    good_name = db.Column(db.String(128), nullable=False)
    images = db.Column(db.PickleType)  # Storing list of images as a PickleType
    price = db.Column(db.Integer, nullable=False)
    owners = db.relationship('User', secondary=users_goods_table, back_populates='goods')

    def serialize(self):
        return {
            'id': self.id,
            'good_name': self.good_name,
            'images': self.images,
            'price': self.price
        }

    def serialize_without_user(self):
        return {
            'id': self.id,
            'good_name': self.good_name,
            'images': self.images,
            'price': self.price
        }

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', back_populates='transactions')

    def serialize(self):
        return {
            'id': self.id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'amount': self.amount,
            'timestamp': self.timestamp.isoformat()
        }

class Rating(db.Model):
    __tablename__ = 'rating'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'))
    transaction = db.relationship('Transaction', back_populates='ratings')

    def serialize(self):
        return {
            'id': self.id,
            'value': self.value,
            'transaction_id': self.transaction_id
        }

# Assuming the Flask app is initialized somewhere else with the database URI,
# you would create the tables in the database with db.create_all() after the
# app has been configured and the context is set up.
