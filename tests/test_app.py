import pytest

import api

@pytest.fixture
def client():
    api.app.config['TESTING'] = True
    client = api.app.test_client()
    yield client

# define tests bellow:
def test_get_no_auth(client):
    response = client.get('/')
    assert response.status_code == 401

def test_get_auth(client):
    response = client.get('/?key=TEST_KEY')
    assert response.status_code == 200
