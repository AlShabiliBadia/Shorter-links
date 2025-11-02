import pytest
import requests
import uuid

@pytest.fixture()
def base_url():
    base_url = "http://0.0.0.0:8000"
    yield base_url


@pytest.fixture()
def authed_user(base_url):
    unique_id = str(uuid.uuid4())
    unique_pass = str(uuid.uuid4())
    email_address = f"{unique_id}@example.com"
    
    signup_payload = {
    "username": "Tester",
    "email": email_address,
    "password" : unique_pass,
    "password_confirmation": unique_pass
    }

    login_payload = {
    "email": email_address,
    "password" : unique_pass,
    }

    requests.post(f'{base_url}/users/signup', json=signup_payload)

    response = requests.post(f'{base_url}/users/login', json=login_payload)
    auth_headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

    yield {"username": "Tester", "email": email_address, "password": unique_pass, "auth_headers": auth_headers}

    requests.delete(f'{base_url}/users/account/delete', headers=auth_headers)


@pytest.fixture()
def created_link(base_url, authed_user):
    payload = {"target_url": "https://github.com/AlShabiliBadia"}

    response = requests.post(f'{base_url}/links/', headers=authed_user["auth_headers"], json=payload)

    
    yield response.json()


@pytest.fixture()
def created_anonymous_link(base_url):
    payload = {"target_url": "https://github.com/AlShabiliBadia"}

    response = requests.post(f'{base_url}/links/', json=payload)

    yield response.json()
