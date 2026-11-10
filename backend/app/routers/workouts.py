
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import get_current_user

router = APIRouter(prefix="/workouts", tags=["Entrenamientos"])


# Consultar los entrenamientos del usuario
@router.get("/", response_model=list[schemas.WorkoutResponse])
def listar_entrenamientos(
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    entrenamientos = db.query(models.Workout).filter(
        models.Workout.user_id == int(usuario_actual)
    ).all()

    return entrenamientos


# Consultar un entrenamiento por su ID
@router.get("/{entrenamiento_id}", response_model=schemas.WorkoutResponse)
def consultar_entrenamiento(
    entrenamiento_id: int,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    entrenamiento = db.query(models.Workout).filter(
        models.Workout.id == entrenamiento_id,
        models.Workout.user_id == int(usuario_actual)
    ).first()

    if not entrenamiento:
        raise HTTPException(
            status_code=404,
            detail="Entrenamiento no encontrado"
        )

    return entrenamiento


# Crear un entrenamiento
@router.post("/", response_model=schemas.WorkoutResponse)
def crear_entrenamiento(
    datos: schemas.WorkoutCreate,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    nuevo_entrenamiento = models.Workout(
        title=datos.title,
        description=datos.description,
        user_id=int(usuario_actual)
    )

    db.add(nuevo_entrenamiento)
    db.commit()
    db.refresh(nuevo_entrenamiento)

    return nuevo_entrenamiento


# Modificar un entrenamiento
@router.put("/{entrenamiento_id}", response_model=schemas.WorkoutResponse)
def modificar_entrenamiento(
    entrenamiento_id: int,
    datos: schemas.WorkoutCreate,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    entrenamiento = db.query(models.Workout).filter(
        models.Workout.id == entrenamiento_id,
        models.Workout.user_id == int(usuario_actual)
    ).first()

    if not entrenamiento:
        raise HTTPException(
            status_code=404,
            detail="Entrenamiento no encontrado"
        )

    entrenamiento.title = datos.title
    entrenamiento.description = datos.description

    db.commit()
    db.refresh(entrenamiento)

    return entrenamiento


# Eliminar un entrenamiento
@router.delete("/{entrenamiento_id}")
def eliminar_entrenamiento(
    entrenamiento_id: int,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    entrenamiento = db.query(models.Workout).filter(
        models.Workout.id == entrenamiento_id,
        models.Workout.user_id == int(usuario_actual)
    ).first()

    if not entrenamiento:
        raise HTTPException(
            status_code=404,
            detail="Entrenamiento no encontrado"
        )

    db.delete(entrenamiento)
    db.commit()

    return {"mensaje": "Entrenamiento eliminado correctamente"}
