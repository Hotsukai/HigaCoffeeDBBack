from datetime import datetime, timezone
from src.app import bcrypt
from src.database import db
from src.models.models import User


def add_sample_users():
    user1 = User(
        name="テストユーザー1",
        encrypted_password=bcrypt.generate_password_hash("password").decode(
            'utf-8'),
    )
    user2 = User(
        name="テストユーザー2",
        encrypted_password=bcrypt.generate_password_hash("password2").decode(
            'utf-8'),
    )
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()
    return user1, user2


def format_datetime_to_json_str(time: datetime):
    return time.astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
