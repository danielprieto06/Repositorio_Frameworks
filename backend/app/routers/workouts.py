
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app import models, schemas
from app.security import get_current_user

router = APIRouter(
    prefix="/workouts",
    tags=["Entrenamientos"]
)


# Consultar los entrenamientos del usuario autenticado
@router.get("/", response_model=list[schemas.WorkoutResponse])
def listar_entrenamientos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    entrenamientos = (
        db.query(models.Workout)
        .filter(models.Workout.user_id == int(usuario_actual))
        .order_by(models.Workout.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

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
@router.post(
    "/",
    response_model=schemas.WorkoutResponse,
    status_code=201
)
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

    try:
        db.add(nuevo_entrenamiento)
        db.commit()
        db.refresh(nuevo_entrenamiento)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se pudo crear el entrenamiento por un conflicto con los datos"
        )

    return nuevo_entrenamiento


# Modificar un entrenamiento
@router.put(
    "/{entrenamiento_id}",
    response_model=schemas.WorkoutResponse
)
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

    try:
        db.commit()
        db.refresh(entrenamiento)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se pudo modificar el entrenamiento"
        )

    return entrenamiento


# Eliminar un entrenamiento
@router.delete(
    "/{entrenamiento_id}",
    status_code=204
)
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

    try:
        db.delete(entrenamiento)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar el entrenamiento porque está relacionado con otros registros"
        )

    return None
