from flask_testing import TestCase

from src.app import app, bcrypt
from src.database import db
from src.models.models import User


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('src.config.TestingConfig')
        return app

    def setUp(self):
        self.app = self.app.test_client()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def addSampleUser(self):
        user1 = User(
            name="テストユーザー1",
            encrypted_password=bcrypt.generate_password_hash(
                "password").decode('utf-8'),
        )
        user2 = User(
            name="テストユーザー2",
            encrypted_password=bcrypt.generate_password_hash(
                "password2").decode('utf-8'),
        )
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
