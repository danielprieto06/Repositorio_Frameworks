
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app import models, schemas
from app.security import get_current_user

router = APIRouter(
    prefix="/progress",
    tags=["Progreso físico"]
)


# Registrar una medición de progreso
@router.post(
    "/",
    response_model=schemas.ProgressResponse,
    status_code=201
)
def registrar_progreso(
    datos: schemas.ProgressCreate,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    nuevo_progreso = models.Progress(
        weight=datos.weight,
        height=datos.height,
        user_id=int(usuario_actual)
    )

    try:
        db.add(nuevo_progreso)
        db.commit()
        db.refresh(nuevo_progreso)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se pudo registrar el progreso por un conflicto con los datos"
        )

    return nuevo_progreso


# Consultar el historial de mediciones del usuario
@router.get(
    "/",
    response_model=list[schemas.ProgressResponse]
)
def listar_progreso(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    progreso = (
        db.query(models.Progress)
        .filter(models.Progress.user_id == int(usuario_actual))
        .order_by(models.Progress.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return progreso


# Consultar la última medición y calcular el IMC
@router.get("/latest")
def consultar_ultimo_progreso(
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    progreso = (
        db.query(models.Progress)
        .filter(models.Progress.user_id == int(usuario_actual))
        .order_by(
            models.Progress.created_at.desc(),
            models.Progress.id.desc()
        )
        .first()
    )

    if not progreso:
        raise HTTPException(
            status_code=404,
            detail="Todavía no hay mediciones registradas"
        )

    # La altura se almacena en centímetros y se convierte a metros
    altura_metros = progreso.height / 100

    imc = progreso.weight / (altura_metros ** 2)

    return {
        "peso": progreso.weight,
        "altura": progreso.height,
        "imc": round(imc, 2),
        "fecha": progreso.created_at
    }
