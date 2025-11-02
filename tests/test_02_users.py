import pytest
import uuid
import requests
from .schemas import *

def test_user_signup_success(base_url):
    unique_id = str(uuid.uuid4())
    unique_pass = str(uuid.uuid4())
    email_address = f"{unique_id}@example.com"
    
    signup_payload = {
    "username": "Tester",
    "email": email_address,
    "password" : unique_pass,
    "password_confirmation": unique_pass
    }

    response = requests.post(f'{base_url}/users/signup', json=signup_payload)


    login_payload = {
    "email": email_address,
    "password" : unique_pass,
    }

    teardown_response = requests.post(f'{base_url}/users/login', json=login_payload)
    teardown_headers = {"Authorization": f"Bearer {teardown_response.json()["access_token"]}"}

    requests.delete(f'{base_url}/users/account/delete', headers=teardown_headers)

    assert response.status_code == 201
    response = response.json()
    try:
        assert UserDisplay.model_validate(response)
    except Exception as e:
        pytest.fail(f"Pydantic validation failed: {e}")
    
def test_signup_existing_email(base_url, authed_user):
    signup_payload = {
    "username": authed_user["username"],
    "email": authed_user["email"],
    "password" : authed_user["password"],
    "password_confirmation": authed_user["password"]
    }

    response = requests.post(f'{base_url}/users/signup', json=signup_payload)

    assert response.status_code == 400

    assert response.json()["detail"] == "An account with this email already exists."

@pytest.mark.parametrize(
    "username, email, password, password_confirmation, expected_status_code", 
    [
        pytest.param("Tester", "test_email@gmail.com", "123456789", "123456781", 422, id="PASSWORD_NO_MATCH"),
        pytest.param("Tester", "not_email", "123456789", "123456789", 422, id="INVALID_EMAIL"),
        pytest.param("Tester", "test_email@gmail.com", "1234", "1234", 422, id="SHORT_PASSWORD"),
        pytest.param("", "test_email@gmail.com", "123456789", "123456781", 422, id="MISSING_USERNAME"),
    ]
)
def test_signup_validation(base_url, username, email, password, password_confirmation, expected_status_code):
    signup_payload = {
    "username": username,
    "email": email,
    "password" : password,
    "password_confirmation": password_confirmation
    }
        
    response = requests.post(f'{base_url}/users/signup', json=signup_payload)

    assert response.status_code == expected_status_code

def test_user_login_success(base_url, authed_user):
    login_payload = {
    "email": authed_user["email"],
    "password" : authed_user["password"],
    }


    response = requests.post(f'{base_url}/users/login', json=login_payload)

    assert response.status_code == 200

    response = response.json()
    try:
        assert Token.model_validate(response)
    except Exception as e:
        pytest.fail(f"Pydantic validation failed: {e}")

def test_user_login_wrong_password(base_url, authed_user):
    login_payload = {
    "email": authed_user["email"],
    "password" : "Wrong_Password",
    }

    response = requests.post(f'{base_url}/users/login', json=login_payload)

    assert response.status_code == 401

def test_delete_account_success(base_url, authed_user):
    login_payload = {
    "email": authed_user["email"],
    "password" : authed_user["password"],
    }
    
    response = requests.delete(f'{base_url}/users/account/delete', headers=authed_user["auth_headers"])
    
    assert response.status_code == 200

    assert response.json()["detail"] == "Account deleted successfully"

    response = requests.post(f'{base_url}/users/login', json=login_payload)

    assert response.status_code == 401

def test_delete_account_no_auth(base_url):
    response = requests.delete(f'{base_url}/users/account/delete')
    
    assert response.status_code == 401