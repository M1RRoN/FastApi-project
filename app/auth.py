import jwt
from datetime import datetime, timedelta

from fastapi import HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, DecodeError, PyJWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.models import User
from app.schemas.users import TokenData
from database.database import SessionLocal

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_jwt_token(username: str) -> str:
    payload = {"username": username}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt_token(token: str, secret_key: str, algorithm: str) -> dict:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except DecodeError:
        raise HTTPException(status_code=401, detail="Token is invalid")


def create_access_token(claims: dict, expires_delta: timedelta):
    expire = datetime.utcnow() + expires_delta
    to_encode = claims.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not pwd_context.verify(password, user.hashed_password):
        return None
    return user


def get_current_active_user(token: str = Header(...)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials"
            )
        token_data = TokenData(username=username)
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    db = SessionLocal()
    user = db.query(User).filter(User.username == token_data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
