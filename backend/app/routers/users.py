
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app import models, schemas
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin
)


router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)


# ==============================
# CONSULTAR PERFIL
# ==============================

@router.get("/me", response_model=schemas.UserResponse)
def consultar_perfil(
    usuario_actual: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    usuario = db.get(models.User, int(usuario_actual))

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    return usuario


# ==============================
# REGISTRAR USUARIO
# ==============================

@router.post(
    "/",
    response_model=schemas.UserResponse,
    status_code=201
)
def registrar_usuario(
    usuario: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    usuario_existente = db.query(models.User).filter(
        models.User.username == usuario.username
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=409,
            detail="El nombre de usuario ya está registrado"
        )

    email_existente = db.query(models.User).filter(
        models.User.email == usuario.email
    ).first()

    if email_existente:
        raise HTTPException(
            status_code=409,
            detail="El correo electrónico ya está registrado"
        )

    nuevo_usuario = models.User(
        username=usuario.username,
        email=usuario.email,
        hashed_password=hash_password(usuario.password),
        role="user"
    )

    try:
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="El nombre de usuario o el correo ya están registrados"
        )

    return nuevo_usuario


# ==============================
# INICIAR SESIÓN
# ==============================

@router.post("/login", response_model=schemas.Token)
def iniciar_sesion(
    datos: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    usuario = db.query(models.User).filter(
        models.User.email == datos.email
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    if not verify_password(
        datos.password,
        usuario.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    token = create_access_token({
        "sub": str(usuario.id)
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ==============================
# ADMINISTRACIÓN DE USUARIOS
# ==============================

# Listar todos los usuarios
@router.get(
    "/admin/users",
    response_model=list[schemas.UserResponse]
)
def listar_usuarios(
    administrador: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    usuarios = db.query(models.User).order_by(
        models.User.id
    ).all()

    return usuarios


# Cambiar el rol de un usuario
@router.patch(
    "/admin/users/{user_id}/role",
    response_model=schemas.UserResponse
)
def cambiar_rol_usuario(
    user_id: int,
    datos: schemas.UserRoleUpdate,
    administrador: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    usuario = db.get(models.User, user_id)

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    # No permitir retirar el último administrador
    if usuario.role == "admin" and datos.role == "user":

        total_administradores = db.query(models.User).filter(
            models.User.role == "admin"
        ).count()

        if total_administradores <= 1:
            raise HTTPException(
                status_code=409,
                detail="No se puede quitar el rol al último administrador"
            )

    usuario.role = datos.role

    db.commit()
    db.refresh(usuario)

    return usuario
