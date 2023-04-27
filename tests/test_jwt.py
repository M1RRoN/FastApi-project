import pytest
from fastapi import HTTPException
import jwt

from app.auth import SECRET_KEY, ALGORITHM, decode_jwt_token


def test_decode_jwt_token_with_valid_token():
    payload = {"sub": "user@example.com"}
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    decoded_payload = decode_jwt_token(access_token, SECRET_KEY, ALGORITHM)
    assert decoded_payload == payload


def test_decode_jwt_token_with_expired_token():
    payload = {"sub": "user@example.com", "exp": 0}
    expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        decode_jwt_token(expired_token, SECRET_KEY, ALGORITHM)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has expired"


def test_decode_jwt_token_with_invalid_token():
    invalid_token = "invalid_token"
    with pytest.raises(HTTPException) as exc_info:
        decode_jwt_token(invalid_token, SECRET_KEY, ALGORITHM)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token is invalid"
