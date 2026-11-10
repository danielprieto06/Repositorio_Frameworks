
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.security import hash_password, verify_password, create_access_token, get_current_user
router = APIRouter(prefix="/users", tags=["Usuarios"])


# Consultar todos los usuarios
@router.get("/", response_model=list[schemas.UserResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    usuarios = db.query(models.User).all()
    return usuarios


# Registrar un usuario
@router.post("/", response_model=schemas.UserResponse)
def registrar_usuario(usuario: schemas.UserCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(models.User).filter(
        models.User.username == usuario.username
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya está registrado"
        )

    email_existente = db.query(models.User).filter(
        models.User.email == usuario.email
    ).first()

    if email_existente:
        raise HTTPException(
            status_code=400,
            detail="El correo electrónico ya está registrado"
        )

    nuevo_usuario = models.User(
        username=usuario.username,
        email=usuario.email,
        hashed_password=hash_password(usuario.password)
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


# Iniciar sesión
@router.post("/login", response_model=schemas.Token)
def iniciar_sesion(datos: schemas.UserLogin, db: Session = Depends(get_db)):
    usuario = db.query(models.User).filter(
        models.User.email == datos.email
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    if not verify_password(datos.password, usuario.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    token = create_access_token({"sub": str(usuario.id)})

    return {
        "access_token": token,
        "token_type": "bearer"
    }
