import pytest
import requests

def test_get_root_status(base_url):
    response = requests.get(base_url)
    assert response.status_code == 200
    assert response.json()["message"] == "URL Shortener API is running."

def test_root_method_not_allowed(base_url):
    response = requests.post(base_url)

    assert response.status_code == 405
