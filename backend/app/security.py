import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User


ALGORITHM = "HS256"

# Permite controlar manualmente los errores cuando falta el token
security = HTTPBearer(auto_error=False)


# Cifrar contraseña con PBKDF2-SHA256
def hash_password(password):
    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        600000
    )

    return salt + "$" + password_hash.hex()


# Comprobar contraseña
def verify_password(password, hashed_password):
    salt, password_hash = hashed_password.split("$")

    new_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        600000
    )

    return secrets.compare_digest(new_hash.hex(), password_hash)


# Crear token JWT con duración de 30 minutos
def create_access_token(data):
    datos = data.copy()

    expiration = datetime.now(timezone.utc) + timedelta(minutes=30)
    datos.update({"exp": expiration})

    token = jwt.encode(
        datos,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# Comprobar que el token JWT es válido
def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    # Comprobar que se ha enviado un token
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="No se ha proporcionado un token de autenticación",
            headers={"WWW-Authenticate": "Bearer"}
        )

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
                detail="Token no válido",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return user_id

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token no válido o caducado",
            headers={"WWW-Authenticate": "Bearer"}
        )


# Comprobar que el usuario tiene permisos de administrador
def require_admin(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        user = db.get(User, int(user_id))
    except (ValueError, TypeError):
        user = None

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado"
        )

    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos de administrador"
        )

    return user
