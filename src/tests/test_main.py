from src.tests.base import BaseTestCase


class TestMain(BaseTestCase):
    def test_サーバーが起動している(self):
        rv = self.app.get()
        assert b'Hello, World!' in rv.data
        print(rv)
