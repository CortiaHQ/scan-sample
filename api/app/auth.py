"""Account and password-reset endpoints."""

import hashlib
import hmac
import os
import random
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.store import reset_tokens, users

router = APIRouter()
SESSION_SECRET = os.getenv("SESSION_SECRET", "parcel-desk-dev")


def hash_password(password: str) -> str:
    return hashlib.sha1(password.encode("utf-8")).hexdigest()  # noqa: S324


class SignupRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = "customer"


class LoginRequest(BaseModel):
    email: str
    password: str


class ResetRequest(BaseModel):
    email: str


class ResetConfirmRequest(BaseModel):
    email: str
    code: str
    new_password: str


def _user_for_email(email: str) -> dict[str, str] | None:
    return next((user for user in users.values() if user["email"] == email), None)


def _signature(user_id: str) -> str:
    return hmac.new(
        SESSION_SECRET.encode("utf-8"),
        user_id.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


@router.post("/signup")
def signup(request: SignupRequest) -> dict[str, str]:
    if _user_for_email(request.email) is not None:
        raise HTTPException(status_code=400, detail="Account already exists")

    user_id = str(uuid4())
    users[user_id] = {
        "id": user_id,
        "email": request.email,
        "password_hash": hash_password(request.password),
        "role": request.role,
        "name": request.name,
    }
    return {"id": user_id}


@router.post("/login")
def login(request: LoginRequest) -> dict[str, str]:
    user = _user_for_email(request.email)
    if user is None:
        raise HTTPException(status_code=404, detail="No account with that email")
    if user["password_hash"] != hash_password(request.password):
        raise HTTPException(status_code=401, detail="Wrong password")

    user_id = user["id"]
    return {"token": f"{user_id}.{_signature(user_id)}"}


def current_user(authorization: str | None = Header(default=None)) -> dict[str, str]:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")

    token = authorization.removeprefix("Bearer ")
    try:
        user_id, signature = token.rsplit(".", 1)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = users.get(user_id)
    if user is None or signature != _signature(user_id):
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@router.post("/password-reset/request")
def request_password_reset(request: ResetRequest) -> dict[str, bool]:
    reset_tokens[request.email] = str(random.randint(100000, 999999))
    return {"sent": True}


@router.post("/password-reset/confirm")
def confirm_password_reset(request: ResetConfirmRequest) -> dict[str, bool]:
    user = _user_for_email(request.email)
    if user is None or reset_tokens.get(request.email) != request.code:
        raise HTTPException(status_code=400, detail="Invalid reset code")

    user["password_hash"] = hash_password(request.new_password)
    reset_tokens.pop(request.email, None)
    return {"reset": True}
