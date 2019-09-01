import pytest
import json
import api

@pytest.fixture
def client():
    api.app.config["TESTING"] = True
    client = api.app.test_client()
    yield client

mimetype = "application/json"

# define tests bellow:

# GET
def test_get_no_auth(client):
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype,
        "Key": ""
    }
    data = {
        "Data": "test"
    }
    url = "/api/"
    response = client.get(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 401

def test_get_auth(client):
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype,
        "Key": "TEST_KEY"
    }
    data = {
        "Data": "test"
    }
    url = "/api/"
    response = client.get(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 200

def test_get_empty(client):
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype,
        "Key": "TEST_KEY"
    }
    data = {
        "Data": ""
    }
    url = "/api/"
    response = client.get(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 204


# POST
def test_post_no_auth(client):
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype,
        "Key": ""
    }
    data = {
        "Data": "test"
    }
    url = "/api/"
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 401

def test_post_auth(client):
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype,
        "Key": "TEST_KEY"
    }
    data = {
        "Data": "test"
    }
    url = "/api/"
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 200

def test_post_empty(client):
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype,
        "Key": "TEST_KEY"
    }
    data = {
        "Data": ""
    }
    url = "/api/"
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 204
