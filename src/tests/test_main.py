import os
import tempfile

import pytest
from main import app


@pytest.fixture
def client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        # with app.app_context():
        #     app.init_db()
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def test_サーバーが起動している(client):
    rv = client.get()
    assert b'Hello, World!' in rv.data
    print(rv)
