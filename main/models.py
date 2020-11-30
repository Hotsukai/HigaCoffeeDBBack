from main import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

class Coffee(db.Model):
    __tablename__ = "coffees"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    powder_amount = db.Column(db.Integer,nullable=False)
    extraction_time = db.Column(db.Integer)
    extraction_method_id = db.Column(db.Integer)
    mesh_id = db.Column(db.Integer)
    water_amount = db.Column(db.Integer)
    water_temperature = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.now(), onupdate=db.func.now())
    bean_id = db.Column(db.Integer,nullable=False)
    dripper_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"),  nullable=False)
    drinker_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"),  nullable=False)
    dripper = db.relationship(
        "User", primaryjoin="Coffee.dripper_id==User.id")
    drinker = db.relationship(
        "User", primaryjoin="Coffee.drinker_id==User.id")
    review_id = db.Column(db.Integer, db.ForeignKey(
        "reviews.id"))

    def __repr__(self):
        return "Coffee(id={})".format(self.id)

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    encrypted_password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.now(), onupdate=db.func.now())
    reviews = db.relationship("Review", backref="user")

    def __repr__(self):
        return "User(id={}, username={})".format(self.id, self.username)

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bitterness = db.Column(db.Integer, nullable=False)
    want_repeat = db.Column(db.Integer, nullable=False)
    situation = db.Column(db.Integer, nullable=False)
    strongness = db.Column(db.Integer, nullable=False)
    feeling = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.now(), onupdate=db.func.now())
    coffee = db.relationship("Coffee", backref="review")
    reviewer_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"),  nullable=False)

    def __repr__(self):
        return "Review(id={}, feeling{})".format(self.id, self.feeling)


BEAN={
    1:{
    "name":"ブラジル深煎り"},
    2:{
    "name":"ブラジル中煎り"},
}

EXTRACTION_METHOD={
    1:{
        "name":"フレンチプレス",
    }
}

MESH={
    1:{
        "name":"粗め"
    }
}

def init():
    db.create_all()
# TODO: seedデータ