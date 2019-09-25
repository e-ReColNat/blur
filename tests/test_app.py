import pytest
import json
import api

@pytest.fixture
def client():
    api.app.config["TESTING"] = True
    client = api.app.test_client()
    yield client

# define tests bellow:

def test_no_auth(client):
    data = "test"
    url = "/api/?source=%s" % (data)
    response = client.get(url)
    assert response.status_code == 401

def test_bad_key(client):
    key = "BAD_KEY"
    data = "test"
    url = "/api/?key=%s&source=%s" % (key, data)
    response = client.get(url)
    assert response.status_code == 401

def test_bad_ip(client):
    key = "TEST_KEY2"
    data = "test"
    url = "/api/?key=%s&source=%s" % (key, data)
    response = client.get(url)
    assert response.status_code == 401

def test_bad_data(client):
    key = "TEST_KEY"
    data = "test"
    url = "/api/?key=%s&source=%s" % (key, data)
    response = client.get(url)
    assert response.status_code == 204

def test_empty_data(client):
    key = "TEST_KEY"
    data = ""
    url = "/api/?key=%s&source=%s" % (key, data)
    response = client.get(url)
    assert response.status_code == 204

def test_bad_url(client):
    key = "TEST_KEY"
    data = "https://www.google.com"
    url = "/api/?key=%s&source=%s" % (key, data)
    response = client.get(url)
    assert response.status_code == 204

def test_get(client):
    key = "TEST_KEY"
    data = "http://mediaphoto.mnhn.fr/media/1441305440248Dg5YP6C3kALFvbh5"
    url = "/api/?key=%s&source=%s" % (key, data)
    response = client.get(url)
    assert response.status_code == 200

def test_flag_confidence(client):
    key = "TEST_KEY"
    data = "http://mediaphoto.mnhn.fr/media/1441305440248Dg5YP6C3kALFvbh5"
    threshold = "0.85"
    url = "/api/?key=%s&source=%s&confidence=%s" % (key, data, threshold)
    response = client.get(url)
    assert response.status_code == 200

def test_flag_debug(client):
    key = "TEST_KEY"
    data = "http://mediaphoto.mnhn.fr/media/1441305440248Dg5YP6C3kALFvbh5"
    threshold = 0.85
    debug = 1
    fileout = 1
    url = "/api/?key=%s&source=%s&confidence=%s&fileout=%s&debug=%s" % (key, data, threshold, fileout, debug)
    response = client.get(url)
    assert response.status_code == 200
