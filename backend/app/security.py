
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings

ALGORITHM = "HS256"

security = HTTPBearer()


def hash_password(password):
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        600000
    )
    return salt + "$" + password_hash.hex()


def verify_password(password, hashed_password):
    salt, password_hash = hashed_password.split("$")
    new_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        600000
    )
    return secrets.compare_digest(new_hash.hex(), password_hash)


def create_access_token(data):
    datos = data.copy()
    expiration = datetime.now(timezone.utc) + timedelta(minutes=30)
    datos.update({"exp": expiration})
    token = jwt.encode(datos, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token


# Comprobar que el token JWT es válido
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        datos = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = datos.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Token no válido"
            )

        return user_id

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token no válido o caducado"
        )
