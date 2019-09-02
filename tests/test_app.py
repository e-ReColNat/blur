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
        "Data": "test"
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
        "Data": "test"
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
        "Data": "test"
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
        "Data": "test",
        "Save_result": False
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
        "Data": "",
        "Save_result": True
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
        "Data": "https://www.google.com",
        "Save_result": False
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
        "Data": "https://upload.wikimedia.org/wikipedia/commons/2/2b/Illustration_Lupinus_luteus1.jpg",
        "Save_result": False
    }
    url = "/api/"
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 200