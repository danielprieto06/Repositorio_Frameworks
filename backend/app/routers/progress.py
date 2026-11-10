
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import get_current_user

router = APIRouter(
    prefix="/progress",
    tags=["Progreso físico"]
)


# Registrar una medición
@router.post("/", response_model=schemas.ProgressResponse)
def registrar_progreso(
    datos: schemas.ProgressCreate,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    if datos.weight <= 0 or datos.height <= 0:
        raise HTTPException(
            status_code=400,
            detail="El peso y la altura deben ser mayores que cero"
        )

    nuevo_progreso = models.Progress(
        weight=datos.weight,
        height=datos.height,
        user_id=int(usuario_actual)
    )

    db.add(nuevo_progreso)
    db.commit()
    db.refresh(nuevo_progreso)

    return nuevo_progreso


# Consultar el historial de mediciones
@router.get("/", response_model=list[schemas.ProgressResponse])
def listar_progreso(
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    progreso = db.query(models.Progress).filter(
        models.Progress.user_id == int(usuario_actual)
    ).order_by(models.Progress.created_at.desc()).all()

    return progreso


# Consultar la última medición y calcular el IMC
@router.get("/latest")
def consultar_ultimo_progreso(
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    progreso = db.query(models.Progress).filter(
        models.Progress.user_id == int(usuario_actual)
    ).order_by(models.Progress.created_at.desc()).first()

    if not progreso:
        raise HTTPException(
            status_code=404,
            detail="Todavía no hay mediciones registradas"
        )

    altura_metros = progreso.height / 100
    imc = progreso.weight / (altura_metros ** 2)

    return {
        "peso": progreso.weight,
        "altura": progreso.height,
        "imc": round(imc, 2),
        "fecha": progreso.created_at
    }
