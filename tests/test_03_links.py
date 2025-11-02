import pytest
import requests
from .schemas import *
import uuid 

def test_create_link_authenticated(base_url, authed_user):
    payload = {"target_url": "https://github.com/AlShabiliBadia"}

    response = requests.post(f'{base_url}/links/', headers=authed_user["auth_headers"], json=payload)

    assert response.status_code == 200

    URLInfo.model_validate(response.json())

def test_create_link_anonymous(base_url):
    payload = {"target_url": "https://github.com/AlShabiliBadia"}

    response = requests.post(f'{base_url}/links/', json=payload)
    
    assert response.status_code == 200

    URLInfo.model_validate(response.json())

def test_create_link_invalid_url(base_url, authed_user):
    payload = {"target_url": "not-a-url"}

    response = requests.post(f'{base_url}/links/', headers=authed_user["auth_headers"], json=payload)

    assert response.status_code == 422

def test_redirect_link(base_url, created_link):

    short_code = created_link["short_url"].split('/')[-1]
    target_url = created_link["target_url"]
    response = requests.get(f"{base_url}/links/{short_code}", allow_redirects=False)
    
    assert response.status_code == 307

    assert response.headers["Location"] == target_url


def test_redirect_not_found(base_url):
    
    response = requests.get(f"{base_url}/links/non-existent-code")
    
    assert response.status_code == 404

    assert response.json()["detail"] == "Link not found!"

def test_link_click_counter(base_url, authed_user, created_link):
    auth_headers = authed_user["auth_headers"]
    short_code = created_link["short_url"].split('/')[-1]

    requests.get(f"{base_url}/links/{short_code}", allow_redirects=True)

    requests.get(f"{base_url}/links/{short_code}", allow_redirects=True)

    response = requests.get(f"{base_url}/links/clicks/{short_code}", headers=auth_headers)

    assert response.status_code == 200

    assert response.json()["clicks"] == 2


def test_get_stats_not_authenticated(base_url, created_link):
    
    short_code = created_link["short_url"].split('/')[-1]

    response = requests.get(f"{base_url}/links/clicks/{short_code}")

    assert response.status_code == 401

def test_get_stats_not_owner(base_url, created_link):
    A_short_code = created_link["short_url"].split('/')[-1]

    unique_id = str(uuid.uuid4())
    unique_pass = str(uuid.uuid4())
    email_address = f"{unique_id}@example.com"
    B_signup_payload = {
    "username": "Tester",
    "email": email_address,
    "password" : unique_pass,
    "password_confirmation": unique_pass
    }

    requests.post(f'{base_url}/users/signup', json=B_signup_payload)


    B_login_payload = {
    "email": email_address,
    "password" : unique_pass,
    }

    B_login_response = requests.post(f'{base_url}/users/login', json=B_login_payload)
    B_headers = {"Authorization": f"Bearer {B_login_response.json()["access_token"]}"}

    response = requests.get(f"{base_url}/links/clicks/{A_short_code}", headers=B_headers)

    assert response.status_code == 403

    requests.delete(f'{base_url}/users/account/delete', headers=B_headers)

def test_get_stats_anonymous_link(base_url, authed_user, created_anonymous_link):
    A_short_code = created_anonymous_link["short_url"].split('/')[-1]
    auth_headers = authed_user["auth_headers"]
    
    response = requests.get(f"{base_url}/links/clicks/{A_short_code}", headers=auth_headers)

    assert response.status_code == 403

