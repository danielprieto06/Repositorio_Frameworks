
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import require_admin

router = APIRouter(prefix="/exercises", tags=["Ejercicios"])


# Consultar todos los ejercicios
# Permite filtrar por grupo muscular
@router.get("/", response_model=list[schemas.ExerciseResponse])
def listar_ejercicios(
    muscle_group: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    consulta = db.query(models.Exercise)

    if muscle_group:
        consulta = consulta.filter(
            models.Exercise.muscle_group.ilike(f"%{muscle_group}%")
        )

    ejercicios = consulta.order_by(models.Exercise.name).offset(skip).limit(limit).all()

    return ejercicios


# Consultar un ejercicio por su ID
@router.get("/{ejercicio_id}", response_model=schemas.ExerciseResponse)
def consultar_ejercicio(
    ejercicio_id: int,
    db: Session = Depends(get_db)
):
    ejercicio = db.query(models.Exercise).filter(
        models.Exercise.id == ejercicio_id
    ).first()

    if not ejercicio:
        raise HTTPException(
            status_code=404,
            detail="Ejercicio no encontrado"
        )

    return ejercicio


# Crear un ejercicio (SOLO ADMINISTRADORES)
@router.post(
    "/",
    response_model=schemas.ExerciseResponse,
    status_code=201
)
def crear_ejercicio(
    datos: schemas.ExerciseCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.User = Depends(require_admin)
):
    nuevo_ejercicio = models.Exercise(
        name=datos.name,
        description=datos.description,
        muscle_group=datos.muscle_group
    )

    db.add(nuevo_ejercicio)
    db.commit()
    db.refresh(nuevo_ejercicio)

    return nuevo_ejercicio


# Modificar un ejercicio (SOLO ADMINISTRADORES)
@router.put(
    "/{ejercicio_id}",
    response_model=schemas.ExerciseResponse
)
def modificar_ejercicio(
    ejercicio_id: int,
    datos: schemas.ExerciseCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.User = Depends(require_admin)
):
    ejercicio = db.query(models.Exercise).filter(
        models.Exercise.id == ejercicio_id
    ).first()

    if not ejercicio:
        raise HTTPException(
            status_code=404,
            detail="Ejercicio no encontrado"
        )

    ejercicio.name = datos.name
    ejercicio.description = datos.description
    ejercicio.muscle_group = datos.muscle_group

    db.commit()
    db.refresh(ejercicio)

    return ejercicio


# Eliminar un ejercicio (SOLO ADMINISTRADORES)
@router.delete("/{ejercicio_id}", status_code=204)
def eliminar_ejercicio(
    ejercicio_id: int,
    db: Session = Depends(get_db),
    usuario_actual: models.User = Depends(require_admin)
):
    ejercicio = db.query(models.Exercise).filter(
        models.Exercise.id == ejercicio_id
    ).first()

    if not ejercicio:
        raise HTTPException(
            status_code=404,
            detail="Ejercicio no encontrado"
        )

    db.delete(ejercicio)
    db.commit()

    return None
