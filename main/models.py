from main import db, app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from enum import IntEnum, Enum, auto
from typing import List, Tuple, Dict
from datetime import datetime

drinkers = db.Table("drinkers",
                    db.Column("coffee_id", db.Integer,
                              db.ForeignKey("coffees.id")),
                    db.Column("drinker_id", db.Integer,
                              db.ForeignKey("users.id"))
                    )


class Coffee(db.Model):
    __tablename__ = "coffees"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.now(), onupdate=db.func.now())
    bean_id = db.Column(db.Integer, nullable=False)
    dripper_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"),  nullable=False)
    dripper = db.relationship(
        "User", primaryjoin="Coffee.dripper_id==User.id")
    drinkers = db.relationship(
        "User", secondary="drinkers")
    extraction_time = db.Column(db.Integer)
    extraction_method_id = db.Column(db.Integer)
    mesh_id = db.Column(db.Integer)
    memo = db.Column(db.Text)
    powder_amount = db.Column(db.Float, nullable=False)
    reviews = db.relationship("Review", back_populates="coffee")
    water_amount = db.Column(db.Integer)
    water_temperature = db.Column(db.Integer)

    def __repr__(self):
        return "Coffee(id={})".format(self.id)

    def to_json(self, with_user=False):
        return{
            "id": self.id,
            "createdAt": self.created_at,
            "bean": BEANS[self.bean_id].to_json(),
            "dripper": self.dripper.to_json() if with_user else None,
            "drinkers": [drinker.to_json() for drinker in self.drinkers] if with_user else None,
            "extractionTime": self.extraction_time,
            "extractionMethod": EXTRACTION_METHOD[self.extraction_method_id] if self.extraction_method_id else None,
            "mesh": MESH[self.mesh_id] if self.mesh_id else None,
            "memo": self.memo,
            "powderAmount": self.powder_amount,
            "reviewId": [review.id for review in self.reviews],
            "waterAmount": self.water_amount,
            "waterTemperature": self.water_temperature,
        }


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    profile = db.Column(db.Text)
    encrypted_password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.now(), onupdate=db.func.now())
    reviews = db.relationship("Review", back_populates="reviewer")
    drink_coffees = db.relationship("Coffee", secondary="drinkers")

    def __repr__(self):
        return "User(id={}, name={})".format(self.id, self.name)

    def to_json(self):
        return {"id": self.id,
                "name": self.name,
                "profile": self.profile,
                "created_at": self.created_at,
                "updated_at": self.updated_at}


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bitterness = db.Column(db.Float, nullable=False)
    want_repeat = db.Column(db.Float, nullable=False)
    situation = db.Column(db.Float, nullable=False)
    strongness = db.Column(db.Float, nullable=False)
    feeling = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.now(), onupdate=db.func.now())
    coffee = db.relationship("Coffee", back_populates="reviews")
    coffee_id = db.Column(db.Integer, db.ForeignKey(
        "coffees.id"),  nullable=False)
    reviewer = db.relationship("User", back_populates="reviews")
    reviewer_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"),  nullable=False)

    def __repr__(self):
        return "Review(id={}, feeling{})".format(self.id, self.feeling)

    def to_json(self, with_user=False):
        return {
            "id": self.id,
            "bitterness": self.bitterness,
            "coffee": self.coffee.to_json(with_user=with_user),
            "feeling": self.feeling,
            "reviewer": self.reviewer.to_json() if with_user else None,
            "situation": self.situation,
            "strongness": self.strongness,
            "wantRepeat": self.want_repeat,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }

    def is_valid(bitterness, situation,   strongness,   want_repeat):
        if bitterness > 4 or bitterness < 0 or \
                strongness > 4 or strongness < 0 or\
                situation > 4 or situation < 0 or\
                want_repeat > 3 or want_repeat < 0:
            return False
        else:
            return True


class Roast(Enum):
    深煎り = 1
    中煎り = 2


class BeanType(Enum):
    ブラジル = 1
    コロンビア = 2
    タンザニア = 3
    マンデリン = 4


class Bean():
    def __init__(self, id: int, name: str, detail: str, roast: Roast, type: BeanType):
        self.id = id
        self.name = name
        self.detail = detail
        self.roast = roast
        self.type = type

    def to_json(self):
        return {
            "id":     self.id,
            "fullName":   self.name,
            "detail": self.detail,
            "roast": {
                "roastID": self.roast.value,
                "roastName": self.roast.name, },
            "BeanType": {
                "BeanTypeID":  self.type.value,
                "BeanTypeName": self.type.name,
            }
        }


BEANS: List[Bean] = [
    Bean(1, "ブラジル深煎り", "ビター 421", Roast.深煎り, BeanType.ブラジル),
    Bean(2, "ブラジル中煎り", "No.2 ｾﾐｳｫｯｼｭﾄﾞ 421", Roast.中煎り, BeanType.ブラジル),
    Bean(3, "コロンビア深煎り", "コロンビア ビター 421", Roast.深煎り, BeanType.コロンビア),
    Bean(4, "コロンビア中煎り", "コロンビア スプレモ 421", Roast.中煎り, BeanType.コロンビア),
    Bean(5, "タンザニア深煎り", "タンザニア ビター 421", Roast.深煎り, BeanType.タンザニア),
    Bean(6, "タンザニア中煎り", "タンザニア キリマンジャロAA 421", Roast.中煎り, BeanType.タンザニア),
    Bean(7, "マンデリン深煎り", "マンデリン ビター 432", Roast.深煎り, BeanType.マンデリン),
    Bean(8, "マンデリン中煎り", "マンデリン G/1 432", Roast.中煎り, BeanType.マンデリン),
]

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


migrate = Migrate(app, db)
