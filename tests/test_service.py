import pytest


def test_data_get(client, init_db):
    response = client.get("/data")
    assert response.status_code == 200
    assert "random_number" in response.get_json()


def test_data_post(client, init_db):
    data = {"key": "value"}
    response = client.post("/data", json=data)
    assert response.status_code == 200
    assert response.get_json() == data


def test_error(client, init_db):
    response = client.get("/error")
    assert response.status_code in [400, 401, 404, 419, 429, 500, 503]
