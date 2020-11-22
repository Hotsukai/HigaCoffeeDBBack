from main import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

class Entry(db.Model):
    __tablename__ = "entries"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"),  nullable=False)  # usersテーブルのidがForeignKey
    user = db.relationship("User")

    def __repr__(self):
        return "Entry(id={} title={!r})".format(self.id, self.title)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    encrypted_password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False,default=db.func.now(), onupdate=db.func.now())
    entry = db.relationship("Entry", uselist=True)

    def __repr__(self):
        return "User(id={}, username={})".format(self.id, self.username)


# class Review(db.Model):
#     __tablename__ = "reviews"
#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     name = db.Column(db.Text, nullable=False, unique=True)
#     encrypted_password = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime(timezone=True), nullable=False)
#     updated_at = db.Column(db.DateTime(timezone=True))
#     entry = db.relationship("Entry", uselist=True)

#     def __repr__(self):
#         return "User(id={}, username={})".format(self.id, self.username)

# class User(db.Model, Us):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     name = db.Column(db.Text, nullable=False, unique=True)
#     encrypted_password = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime(timezone=True), nullable=False)
#     updated_at = db.Column(db.DateTime(timezone=True))
#     entry = db.relationship("Entry", uselist=True)

#     def __repr__(self):
#         return "User(id={}, username={})".format(self.id, self.username)


def init():
    db.create_all()
