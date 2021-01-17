import json

from src.tests.base import BaseTestCase


class TestMain(BaseTestCase):
    def test_サーバーが起動している(self):
        response = self.app.get("/")
        self.assert_200(response)
        assert b'Hello, World!' in response.data

    def test_豆の種類APIの戻り値がフロントが予期する形式(self):
        response = self.app.get("/beans")
        self.assert_200(response)
        data = json.loads(response.get_data())
        assert data["result"] is True
        for bean in data["data"]:
            assert bean["fullName"] is not None
            assert bean["id"] is not None
            assert bean["detail"] is not None
            assert bean["roast"]["id"] is not None
            assert bean["roast"]["name"] is not None
            assert bean["origin"]["id"] is not None
            assert bean["origin"]["name"] is not None
