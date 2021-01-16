import json

from src.tests.base import BaseTestCase


class TestUser(BaseTestCase):
    def test_ログインできる(self):
        self.addSampleUser()
        response = self.app.post("auth/login",
                                 data=json.dumps({
                                     "username": "テストユーザー1",
                                     "password": "password"
                                 }),
                                 content_type='application/json')

        self.assert200(response)
        data = json.loads(response.get_data())
        assert data["result"] is True
        assert data["token"] != ""
        assert data["data"]["name"] != ""

    def test_不正なリクエストではログインできない(self):
        self.addSampleUser()
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
            data = json.loads(response.get_data())
            assert data["result"] is False
            assert data["message"] == case["expect_response_data"]["message"]
            assert "token" not in data
