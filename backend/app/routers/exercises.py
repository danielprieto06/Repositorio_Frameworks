
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import get_current_user

router = APIRouter(prefix="/exercises", tags=["Ejercicios"])


# Consultar todos los ejercicios
@router.get("/", response_model=list[schemas.ExerciseResponse])
def listar_ejercicios(db: Session = Depends(get_db)):
    ejercicios = db.query(models.Exercise).all()
    return ejercicios


# Consultar un ejercicio por su ID
@router.get("/{ejercicio_id}", response_model=schemas.ExerciseResponse)
def consultar_ejercicio(ejercicio_id: int, db: Session = Depends(get_db)):
    ejercicio = db.query(models.Exercise).filter(
        models.Exercise.id == ejercicio_id
    ).first()

    if not ejercicio:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")

    return ejercicio


# Crear un ejercicio
@router.post("/", response_model=schemas.ExerciseResponse)
def crear_ejercicio(
    datos: schemas.ExerciseCreate,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
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


# Modificar un ejercicio
@router.put("/{ejercicio_id}", response_model=schemas.ExerciseResponse)
def modificar_ejercicio(
    ejercicio_id: int,
    datos: schemas.ExerciseCreate,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    ejercicio = db.query(models.Exercise).filter(
        models.Exercise.id == ejercicio_id
    ).first()

    if not ejercicio:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")

    ejercicio.name = datos.name
    ejercicio.description = datos.description
    ejercicio.muscle_group = datos.muscle_group

    db.commit()
    db.refresh(ejercicio)

    return ejercicio


# Eliminar un ejercicio
@router.delete("/{ejercicio_id}")
def eliminar_ejercicio(
    ejercicio_id: int,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    ejercicio = db.query(models.Exercise).filter(
        models.Exercise.id == ejercicio_id
    ).first()

    if not ejercicio:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")

    db.delete(ejercicio)
    db.commit()

    return {"mensaje": "Ejercicio eliminado correctamente"}
