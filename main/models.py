from main import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


class Entry(db.Model):  # 実験用
    __tablename__ = "entries"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"),  nullable=False)  # usersテーブルのidがForeignKey
 

    def __repr__(self):
        return "Entry(id={} title={!r})".format(self.id, self.title)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    encrypted_password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.now(), onupdate=db.func.now())
    entrys = db.relationship("Entry", backref="user")
    reviews = db.relationship("Review", backref="user")
    dripped_coffees = db.relationship("Coffee", backref="user")
    dripping_coffees = db.relationship("Coffee", backref="user")

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

    def __repr__(self):
        return "Review(id={}, feeling{})".format(self.id, self.feeling)


class Coffee(db.Model):
    __tablename__ = "coffees"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    powder_amount = db.Column(db.Integer)
    extraction_time = db.Column(db.Integer, nullable=False)
    extraction_method_id = db.Column(db.Integer, db.ForeignKey(
        "extraction_methods.id"),  nullable=False)
    water_amount = db.Column(db.Integer)
    water_temperature = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.now(), onupdate=db.func.now())
    bean_id = db.Column(db.Integer, db.ForeignKey(
        "beans.id"),  nullable=False)
    mesh_id = db.Column(db.Integer, db.ForeignKey(
        "mesh.id"))
    dripper_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"),  nullable=False)
    drinker_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"),  nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey(
        "coffees.id"))

    def __repr__(self):
        return "Coffee(id={})".format(self.id)


class Bean(db.Model):
    __tablename__ = "beans"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False, unique=True)
    coffees = db.relationship("Coffee", backref="bean")

    def __repr__(self):
        return "Beane(id={},name={})".format(self.id, self.name)


class Extraction_method(db.Model):
    __tablename__ = "extraction_methods"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False, unique=True)
    coffees = db.relationship("Coffee", backref="extraction_method")

    def __repr__(self):
        return "Beane(id={},name={})".format(self.id, self.name)


class Mesh(db.Model):
    __tablename__ = "mesh"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    coffees = db.relationship("Coffee", backref="extraction_method")



def init():
    db.create_all()
