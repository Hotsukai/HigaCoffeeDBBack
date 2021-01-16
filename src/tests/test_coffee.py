import json

from src.tests.base import BaseTestCase
valid_coffee_param = {
    "beanId": 2,
    "drinkerIds": [1],
    "dripperId": 1,
    "extractionMethodId": 1,
    "extractionTime": 8,
    "memo": "",
    "meshId": None,
    "powderAmount": 8.7,
    "waterAmount": 98,
    "waterTemperature": 3,
}


class TestCoffee(BaseTestCase):
    def test_はじめはデータがない(self):
        response = self.app.get("coffees")
        body = json.loads(response.get_data())
        self.assert_200(response)
        print(body)
        assert body["result"] is True
        assert len(body["data"]) == 0

    def test_ログインなしで追加できない(self):
        postParams = {}
        response = self.app.post("coffees",
                                 data=json.dumps(postParams),
                                 content_type='application/json')

        self.assert401(response)

    def test_正常な追加できない(self):
        postParams = {
            "beanId": 2,
            "drinkerIds": [3],
            "dripperId": 1,
            "extractionMethodId": 1,
            "extractionTime": 8,
            "memo": "",
            "meshId": None,
            "powderAmount": 8.7,
            "waterAmount": 98,
            "waterTemperature": 3,
        }
        response = self.app.post("coffees",
                                 data=json.dumps(postParams),
                                 content_type='application/json')

        self.assert_status(response, 401)
