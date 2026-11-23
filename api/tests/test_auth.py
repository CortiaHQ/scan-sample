import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def account(client):
    account = {
        "email": f"auth-test-{uuid.uuid4().hex}@example.com",
        "password": "original-password",
        "name": "Auth Test User",
    }
    response = client.post("/auth/signup", json=account)
    assert response.status_code in (200, 201), response.text
    return account


def sign_in(client, email, password):
    return client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )


def test_signup_then_signin_issues_token(client, account):
    response = sign_in(client, account["email"], account["password"])

    assert response.status_code == 200, response.text
    assert response.json()["access_token"]


def test_signin_rejects_wrong_password(client, account):
    response = sign_in(client, account["email"], "not-the-password")

    assert response.status_code == 401


def test_signin_rejects_unknown_email(client):
    response = sign_in(
        client, f"unknown-{uuid.uuid4().hex}@example.com", "any-password"
    )

    assert response.status_code in (401, 404)


def test_current_user_accepts_valid_token_and_rejects_tampering(client, account):
    login = sign_in(client, account["email"], account["password"])
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    response = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    assert response.json()["email"] == account["email"]

    parts = token.split(".")
    if len(parts) > 1:
        last = parts[-1]
        parts[-1] = ("A" if last[0] != "A" else "B") + last[1:]
        tampered = ".".join(parts)
    else:
        tampered = ("A" if token[0] != "A" else "B") + token[1:]

    response = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {tampered}"}
    )
    assert response.status_code == 401


def test_password_reset_code_changes_password(client, account):
    response = client.post(
        "/auth/reset/request", json={"email": account["email"]}
    )
    assert response.status_code in (200, 201), response.text

    code = response.json().get("code")
    if code is None:
        from app import store

        codes = getattr(store, "reset_codes", None)
        if codes is None:
            codes = getattr(store, "RESET_CODES")
        entry = codes[account["email"]]
        code = entry["code"] if isinstance(entry, dict) else entry

    new_password = "replacement-password"
    response = client.post(
        "/auth/reset/confirm",
        json={
            "email": account["email"],
            "code": code,
            "new_password": new_password,
        },
    )
    assert response.status_code in (200, 204), response.text

    old_login = sign_in(client, account["email"], account["password"])
    assert old_login.status_code == 401

    new_login = sign_in(client, account["email"], new_password)
    assert new_login.status_code == 200, new_login.text
    assert new_login.json()["access_token"]