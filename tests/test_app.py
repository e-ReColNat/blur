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

# POST
def test_post_no_auth(client):
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype,
        "Key": ""
    }
    data = {
        "data": "test"
    }
    url = "/api/"
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 401

def test_get_bad_key(client):
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype,
        "Key": "BAD_KEY"
    }
    data = {
        "data": "test"
    }
    url = "/api/"
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 401

def test_get_bad_ip(client):
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype,
        "Key": "TEST_KEY2"
    }
    data = {
        "data": "test"
    }
    url = "/api/"
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 401

def test_post_bad_data(client):
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype,
        "Key": "TEST_KEY"
    }
    data = {
        "data": "test",
    }
    url = "/api/"
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 204

def test_post_empty_data(client):
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype,
        "Key": "TEST_KEY"
    }
    data = {
        "data": "",
    }
    url = "/api/"
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 204

def test_post_bad_url(client):
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype,
        "Key": "TEST_KEY"
    }
    data = {
        "data": "https://www.google.com",
    }
    url = "/api/"
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 204

def test_post(client):
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype,
        "Key": "TEST_KEY"
    }
    data = {
        "data": "http://mediaphoto.mnhn.fr/media/1441305440248Dg5YP6C3kALFvbh5",
    }
    url = "/api/"
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 200
