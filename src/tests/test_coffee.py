from typing import Dict

from flask import json as flask_json
from flask_jwt_extended import create_access_token

from src.models.models import BEANS, Coffee, EXTRACTION_METHOD
from src.database import db
from .base import BaseTestCase
from .test_utils import add_sample_users, format_datetime_to_json_str


class TestCoffee(BaseTestCase):
    def test_ログインなしで登録できない(self):
        postParams = {}
        response = self.app.post("coffees",
                                 data=flask_json.dumps(postParams),
                                 content_type='application/json')

        self.assert401(response)

    def test_コーヒーが登録できる(self):
        user1, user2 = add_sample_users()
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
                                 data=flask_json.dumps(postParams),
                                 headers={"Authorization": f"Bearer {token}"},
                                 content_type='application/json')
        self.assert_status(response, 200)
        coffee: Coffee = Coffee.query.get(1)
        data = flask_json.loads(response.get_data())
        assert data == {
            'data': {
                "bean":
                BEANS[0].to_json(),
                'createdAt':
                format_datetime_to_json_str(coffee.created_at),
                'drinkers': [{
                    'created_at':
                    format_datetime_to_json_str(user1.created_at),
                    'id':
                    user1.id,
                    'name':
                    user1.name,
                    'profile':
                    user1.profile,
                    'updated_at':
                    format_datetime_to_json_str(user1.updated_at)
                }, {
                    'created_at':
                    format_datetime_to_json_str(user2.created_at),
                    'id':
                    user2.id,
                    'name':
                    user2.name,
                    'profile':
                    user2.profile,
                    'updated_at':
                    format_datetime_to_json_str(user2.updated_at)
                }],
                'dripper': {
                    'created_at':
                    format_datetime_to_json_str(user1.created_at),
                    'id': user1.id,
                    'name': user1.name,
                    'profile': user1.profile,
                    'updated_at': format_datetime_to_json_str(user1.updated_at)
                },
                'extractionMethod':
                EXTRACTION_METHOD[1],
                'extractionTime':
                coffee.extraction_time,
                'id':
                coffee.id,
                'memo':
                coffee.memo,
                'mesh':
                coffee.mesh_id,
                'powderAmount':
                coffee.powder_amount,
                'reviewId': [],
                'reviews': [],
                'waterAmount':
                coffee.water_amount,
                'waterTemperature':
                coffee.water_temperature
            },
            'message': 'コーヒーを作成しました。',
            'result': True
        }

    def test_ログイン無しでコーヒーを1件取得できる(self):
        user1, user2 = add_sample_users()
        coffee = Coffee(bean_id=1,
                        dripper_id=user1.id,
                        extraction_time=4,
                        extraction_method_id=1,
                        mesh_id=None,
                        memo="memo",
                        powder_amount=10,
                        water_amount=120,
                        water_temperature=90)
        coffee.drinkers.append(user2)
        db.session.add(coffee)
        db.session.commit()

        response = self.app.get("/coffees/1")
        self.assert_200(response)
        data_dict = flask_json.loads(response.get_data())
        assert data_dict == {
            'data': {
                'bean': BEANS[0].to_json(),
                'createdAt': format_datetime_to_json_str(coffee.created_at),
                'drinkers': None,
                'dripper': None,
                'extractionMethod': EXTRACTION_METHOD[1],
                'extractionTime': coffee.extraction_time,
                'id': coffee.id,
                'memo': coffee.memo,
                'mesh': coffee.mesh_id,
                'powderAmount': coffee.powder_amount,
                'reviewId': [],
                'reviews': [],
                'waterAmount': coffee.water_amount,
                'waterTemperature': coffee.water_temperature
            },
            'result': True
        }

    def test_ログイン時ユーザー情報ありでコーヒーを1件取得できる(self):
        user1, user2 = add_sample_users()
        coffee = Coffee(bean_id=1,
                        dripper_id=user1.id,
                        drinkers=[user1, user2],
                        extraction_time=4,
                        extraction_method_id=1,
                        mesh_id=None,
                        memo="memo",
                        powder_amount=10,
                        water_amount=120,
                        water_temperature=90)
        db.session.add(coffee)
        db.session.commit()
        token: str = create_access_token(user1)

        response = self.app.get(
            "coffees/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assert_200(response)
        data_dict = flask_json.loads(response.get_data())
        assert data_dict == {
            'data': {
                "bean":
                BEANS[0].to_json(),
                'createdAt':
                format_datetime_to_json_str(coffee.created_at),
                'drinkers': [{
                    'created_at':
                    format_datetime_to_json_str(user1.created_at),
                    'id':
                    user1.id,
                    'name':
                    user1.name,
                    'profile':
                    user1.profile,
                    'updated_at':
                    format_datetime_to_json_str(user1.updated_at)
                }, {
                    'created_at':
                    format_datetime_to_json_str(user2.created_at),
                    'id':
                    user2.id,
                    'name':
                    user2.name,
                    'profile':
                    user2.profile,
                    'updated_at':
                    format_datetime_to_json_str(user2.updated_at)
                }],
                'dripper': {
                    'created_at':
                    format_datetime_to_json_str(user1.created_at),
                    'id': user1.id,
                    'name': user1.name,
                    'profile': user1.profile,
                    'updated_at': format_datetime_to_json_str(user1.updated_at)
                },
                'extractionMethod':
                EXTRACTION_METHOD[1],
                'extractionTime':
                coffee.extraction_time,
                'id':
                coffee.id,
                'memo':
                coffee.memo,
                'mesh':
                coffee.mesh_id,
                'powderAmount':
                coffee.powder_amount,
                'reviewId': [],
                'reviews': [],
                'waterAmount':
                coffee.water_amount,
                'waterTemperature':
                coffee.water_temperature
            },
            'result': True
        }

    def test_コーヒーは一度に10件取得できる(self):
        user1, user2 = add_sample_users()
        for i in range(20):
            coffee = Coffee(bean_id=1,
                            dripper_id=user1.id,
                            drinkers=[user1, user2],
                            extraction_time=4,
                            extraction_method_id=1,
                            mesh_id=None,
                            memo="memo",
                            powder_amount=10,
                            water_amount=120,
                            water_temperature=90)
            db.session.add(coffee)
        db.session.commit()
        token: str = create_access_token(user1)

        response = self.app.get(
            "coffees",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assert_200(response)
        res_data: Dict = flask_json.loads(response.get_data())
        # datetimeをStringにするためにPythonDict -> String -> 
        want_data: Dict = flask_json.loads(
            flask_json.dumps({
                'data': [
                    coffee.to_json(with_user=True)
                    for coffee in Coffee.query.all()[0:10]
                ],
                'result':
                True,
                "existMore":
                True
            }))
        assert want_data == res_data

        response = self.app.get("coffees",
                                headers={"Authorization": f"Bearer {token}"},
                                query_string={"offset": 10})
        self.assert_200(response)
        res_data: Dict = flask_json.loads(response.get_data())
        want_data: Dict = flask_json.loads(
            flask_json.dumps({
                'data': [
                    coffee.to_json(with_user=True)
                    for coffee in Coffee.query.all()[10:20]
                ],
                'result':
                True,
                "existMore":
                False
            }))
        assert want_data == res_data
