import json

from flask_jwt_extended import create_access_token

from src.models.models import BEANS
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
    def test_ログインなしで追加できない(self):
        postParams = {}
        response = self.app.post("coffees",
                                 data=json.dumps(postParams),
                                 content_type='application/json')

        self.assert401(response)

    def test_コーヒーが登録できる(self):
        user1, _ = self.addSampleUser()
        token: str = create_access_token(user1)
        postParams = {
            "beanId": 1,
            "drinkerIds": [1, 2],
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
                                 headers={"Authorization": f"Bearer {token}"},
                                 content_type='application/json')
        self.assert_status(response, 200)
        data = json.loads(response.get_data())
        _bean = list(
            filter(lambda bean: bean.id == postParams["beanId"], BEANS))[0]
        assert data['result'] is True
        assert data['data']["id"] == 1
        assert data['data']["bean"]["fullName"] == _bean.name
        assert data['data']["bean"]["detail"] == _bean.detail
        assert data['data']["bean"]["roast"]["id"] == _bean.roast.value
        assert data['data']["bean"]["roast"]["name"] == _bean.roast.name
        assert data['data']["bean"]["origin"]["id"] == _bean.origin.value
        assert data['data']["bean"]["origin"]["name"] == _bean.origin.name
