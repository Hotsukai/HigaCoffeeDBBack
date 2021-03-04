from datetime import timezone
import json
from operator import add

from flask_jwt_extended import create_access_token

from src.models.models import BEANS, Coffee
from src.database import db
from .base import BaseTestCase
from .test_utils import add_sample_users, format_datetime_to_json_str

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
        user1, _ = add_sample_users()
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

    def test_ログイン無しでコーヒーを1件取得できる(self):
        user1, user2 = add_sample_users()
        coffee1 = Coffee(bean_id=1,
                         dripper_id=user1.id,
                         extraction_time=4,
                         extraction_method_id=1,
                         mesh_id=None,
                         memo="memo",
                         powder_amount=10,
                         water_amount=120,
                         water_temperature=90)
        coffee1.drinkers.append(user2)
        db.session.add(coffee1)
        db.session.commit()

        response = self.app.get("/coffees/1")
        self.assert_200(response)
        data_dict = json.loads(response.get_data())
        assert data_dict == {
            'data': {
                'bean': {
                    'detail': 'ビター 421',
                    'fullName': 'ブラジル深煎り',
                    'id': 1,
                    'origin': {
                        'id': 1,
                        'name': 'ブラジル'
                    },
                    'roast': {
                        'id': 1,
                        'name': '深煎り'
                    }
                },
                'createdAt': format_datetime_to_json_str(coffee1.created_at),
                'drinkers': None,
                'dripper': None,
                'extractionMethod': {
                    'id': 1,
                    'name': 'フレンチプレス'
                },
                'extractionTime': 4,
                'id': 1,
                'memo': 'memo',
                'mesh': None,
                'powderAmount': 10.0,
                'reviewId': [],
                'reviews': [],
                'waterAmount': 120,
                'waterTemperature': 90
            },
            'result': True
        }
