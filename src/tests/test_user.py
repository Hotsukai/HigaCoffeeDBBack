import json

from flask_jwt_extended.utils import create_access_token

from src.tests.base import BaseTestCase
from src.app import WATCH_WORD
from src.models.models import User
from .test_utils import add_sample_users, format_datetime_to_json_str


class TestUser(BaseTestCase):
    def test_ログインできる(self):
        user1: User
        user1, _ = add_sample_users()

        response = self.app.post("auth/login",
                                 data=json.dumps({
                                     "username": user1.name,
                                     "password": "password"
                                 }),
                                 content_type='application/json')

        self.assert200(response)
        data = json.loads(response.get_data())
        assert data == {
            'data': {
                'created_at': format_datetime_to_json_str(user1.created_at),
                'id': user1.id,
                'name': user1.name,
                'profile': user1.profile,
                'updated_at': format_datetime_to_json_str(user1.updated_at)
            },
            'message': f'ユーザー({user1.name})のログインに成功しました。',
            'result': True,
            'token': data["token"]
        }

    def test_不正なリクエストではログインできない(self):
        add_sample_users()
        cases = [{
            "form_data": {
                "username": "テストユーザー3",
                "password": "password"
            },
            "expect_response_data": {
                "status_code": 401,
                "message": "ユーザー(テストユーザー3)は登録されていません"
            }
        }, {
            "form_data": {
                "password": "password"
            },
            "expect_response_data": {
                "status_code": 400,
                "message": "ユーザー名は必須です"
            }
        }, {
            "form_data": {
                "username": "テストユーザー1",
            },
            "expect_response_data": {
                "status_code": 400,
                "message": "パスワードは必須です"
            }
        }, {
            "form_data": {
                "username": "テストユーザー1",
                "password": "invalid_password"
            },
            "expect_response_data": {
                "status_code": 401,
                "message": "ユーザー(テストユーザー1)のパスワードが間違っています"
            }
        }]
        for case in cases:
            response = self.app.post("auth/login",
                                     data=json.dumps(case["form_data"]),
                                     content_type='application/json')
            assert response.status_code == case["expect_response_data"][
                "status_code"]
            assert json.loads(response.get_data()) == {
                "result": False,
                "message": case["expect_response_data"]["message"]
            }

    def test_新規登録できる(self):
        response = self.app.post("auth/create_user",
                                 data=json.dumps({
                                     "username": "テストユーザー1",
                                     "password": "password",
                                     "watchword": WATCH_WORD
                                 }),
                                 content_type='application/json')
        assert response.status_code == 201
        user: User = User.query.get(1)
        data = json.loads(response.get_data())
        assert data == {
            'data': {
                'created_at': format_datetime_to_json_str(user.created_at),
                'id': user.id,
                'name': user.name,
                'profile': user.profile,
                'updated_at': format_datetime_to_json_str(user.updated_at)
            },
            'message': f'ユーザー({user.name})を作成しました。',
            'result': True,
            'token': data["token"]
        }

    def test_不正なリクエストでは新規登録できない(self):
        add_sample_users()
        cases = [{
            "form_data": {
                "username": "テストユーザー3",
                "password": "password",
                "watchword": "invalid_watchword"
            },
            "expect_response_data": {
                "status_code": 401,
                "message": "合言葉が違います"
            }
        }, {
            "form_data": {
                "username": "テストユーザー3",
                "password": "password",
            },
            "expect_response_data": {
                "status_code": 401,
                "message": "合言葉が違います"
            }
        }, {
            "form_data": {
                "password": "password",
                "watchword": WATCH_WORD
            },
            "expect_response_data": {
                "status_code": 400,
                "message": "ユーザー名は必須です"
            }
        }, {
            "form_data": {
                "username": "テストユーザー1",
                "password": "password",
                "watchword": WATCH_WORD
            },
            "expect_response_data": {
                "status_code": 409,
                "message": "ユーザー名が利用されています"
            }
        }, {
            "form_data": {
                "username": "a" * 31,
                "password": "password",
                "watchword": WATCH_WORD
            },
            "expect_response_data": {
                "status_code": 400,
                "message": "ユーザー名が長すぎます"
            }
        }, {
            "form_data": {
                "username": "テストユーザー3",
                "password": "a" * 51,
                "watchword": WATCH_WORD
            },
            "expect_response_data": {
                "status_code": 400,
                "message": "パスワードが長すぎます"
            }
        }]
        for case in cases:
            response = self.app.post("auth/create_user",
                                     data=json.dumps(case["form_data"]),
                                     content_type='application/json')
            assert response.status_code == case["expect_response_data"][
                "status_code"]
            data = json.loads(response.get_data())
            assert data == {
                "result": False,
                "message": case["expect_response_data"]["message"]
            }

    def test_ログインなしでユーザー情報は見れない(self):
        response = self.app.get("users/1")
        assert response.status_code == 401
        assert json.loads(response.get_data()) == {
            "result": False,
            "message": "ログインが必要です",
            "data": {}
        }
        assert json.loads(response.get_data()) == {
            "result": False,
            "message": "ログインが必要です",
            "data": {}
        }

    def test_ログインなしでユーザー検索はできない(self):
        response = self.app.get("users", query_string={"name": "テストユーザー1"})
        assert response.status_code == 401
        assert json.loads(response.get_data()) == {
            "result": False,
            "message": "ログインが必要です",
            "data": {}
        }

    def test_ログインすればユーザー情報が見れる(self):
        user1, user2 = add_sample_users()
        token: str = create_access_token(user1)
        response = self.app.get(
            "users/2",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = json.loads(response.get_data())
        assert data == {
            'data': {
                'created_at': format_datetime_to_json_str(user2.created_at),
                'id': user2.id,
                'name': user2.name,
                'profile': user2.profile,
                'updated_at': format_datetime_to_json_str(user2.updated_at),
            },
            'message': None,
            'result': True
        }

    def test_ログインすればユーザー検索ができる(self):
        user1, _ = add_sample_users()
        token: str = create_access_token(user1)
        response = self.app.get(
            "users",
            query_string={"name": "テストユーザー1"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert json.loads(response.get_data()) == {
            'data': [{
                'id': 1,
                'name': 'テストユーザー1'
            }],
            'message': None,
            'result': True
        }
