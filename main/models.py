from main import db, app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_migrate import Migrate

drinkers = db.Table("drinkers",
                    db.Column("coffee_id", db.Integer,
                              db.ForeignKey("coffees.id")),
                    db.Column("drinker_id", db.Integer,
                              db.ForeignKey("users.id"))
                    )


class Coffee(db.Model):
    __tablename__ = "coffees"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    powder_amount = db.Column(db.Integer, nullable=False)
    extraction_time = db.Column(db.Integer)
    extraction_method_id = db.Column(db.Integer)
    mesh_id = db.Column(db.Integer)
    water_amount = db.Column(db.Integer)
    water_temperature = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False,
    
                           default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.now(), onupdate=db.func.now())
    bean_id = db.Column(db.Integer, nullable=False)
    memo = db.Column(db.Text)
    dripper_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"),  nullable=False)
    dripper = db.relationship(
        "User", primaryjoin="Coffee.dripper_id==User.id")
    drinker = db.relationship(
        "User", secondary="drinkers")
    reviews = db.relationship("Review", backref="coffees")

    def __repr__(self):
        return "Coffee(id={})".format(self.id)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    profile = db.Column(db.Text)
    encrypted_password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.now(), onupdate=db.func.now())
    reviews = db.relationship("Review", backref="users")
    drink_coffees = db.relationship("Coffee", secondary="drinkers")

    def __repr__(self):
        return "User(id={}, name={})".format(self.id, self.name)


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
    coffee_id = reviewer_id = db.Column(db.Integer, db.ForeignKey(
        "coffees.id"),  nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"),  nullable=False)

    def __repr__(self):
        return "Review(id={}, feeling{})".format(self.id, self.feeling)


BEAN = {
    1: {
        "id": 1,
        "name": "ブラジル深煎り"
    },
    2: {
        "id": 2,
        "name": "ブラジル中煎り"
    },
}

EXTRACTION_METHOD = {
    1: {
        "id": 1,
        "name": "フレンチプレス",
    },
}

MESH = {
    1: {
        "id": 1,
        "name": "粗め"
    },
    2: {
        "id": 2,
        "name": "やや粗め"
    },
}

# TODO: seedデータ

migrate = Migrate(app, db)
