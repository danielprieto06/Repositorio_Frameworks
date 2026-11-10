
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.database import get_db
from app import models, schemas
from app.security import get_current_user

router = APIRouter(
    prefix="/food-entries",
    tags=["Nutrición - Registro de comidas"]
)


# Consultar los registros de alimentación del usuario
@router.get("/", response_model=list[schemas.FoodEntryResponse])
def listar_comidas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    comidas = (
        db.query(models.FoodEntry)
        .filter(models.FoodEntry.user_id == int(usuario_actual))
        .order_by(models.FoodEntry.consumed_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return comidas


# Consultar el resumen diario de calorías
@router.get("/daily-summary")
def resumen_diario(
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    hoy = datetime.now(timezone.utc).date()

    total_calorias = db.query(
        func.coalesce(
            func.sum(models.FoodEntry.calories_total),
            0
        )
    ).filter(
        models.FoodEntry.user_id == int(usuario_actual),
        func.date(models.FoodEntry.consumed_at) == hoy
    ).scalar()

    return {
        "fecha": str(hoy),
        "calorias_consumidas": round(float(total_calorias), 2)
    }


# Consultar un registro de comida por su ID
@router.get(
    "/{comida_id}",
    response_model=schemas.FoodEntryResponse
)
def consultar_comida(
    comida_id: int,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    comida = db.query(models.FoodEntry).filter(
        models.FoodEntry.id == comida_id,
        models.FoodEntry.user_id == int(usuario_actual)
    ).first()

    if not comida:
        raise HTTPException(
            status_code=404,
            detail="Comida no encontrada"
        )

    return comida


# Registrar una comida
@router.post(
    "/",
    response_model=schemas.FoodEntryResponse,
    status_code=201
)
def registrar_comida(
    datos: schemas.FoodEntryCreate,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    alimento = db.query(models.Food).filter(
        models.Food.id == datos.food_id
    ).first()

    if not alimento:
        raise HTTPException(
            status_code=404,
            detail="Alimento no encontrado"
        )

    calorias = alimento.calories * datos.quantity_g / 100

    nueva_comida = models.FoodEntry(
        user_id=int(usuario_actual),
        food_id=datos.food_id,
        quantity_g=datos.quantity_g,
        calories_total=calorias
    )

    try:
        db.add(nueva_comida)
        db.commit()
        db.refresh(nueva_comida)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se pudo registrar la comida por un conflicto con los datos"
        )

    return nueva_comida


# Modificar un registro de comida
@router.put(
    "/{comida_id}",
    response_model=schemas.FoodEntryResponse
)
def modificar_comida(
    comida_id: int,
    datos: schemas.FoodEntryCreate,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    comida = db.query(models.FoodEntry).filter(
        models.FoodEntry.id == comida_id,
        models.FoodEntry.user_id == int(usuario_actual)
    ).first()

    if not comida:
        raise HTTPException(
            status_code=404,
            detail="Comida no encontrada"
        )

    alimento = db.query(models.Food).filter(
        models.Food.id == datos.food_id
    ).first()

    if not alimento:
        raise HTTPException(
            status_code=404,
            detail="Alimento no encontrado"
        )

    comida.food_id = datos.food_id
    comida.quantity_g = datos.quantity_g
    comida.calories_total = (
        alimento.calories * datos.quantity_g / 100
    )

    try:
        db.commit()
        db.refresh(comida)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se pudo modificar el registro de comida"
        )

    return comida


# Eliminar un registro de comida
@router.delete(
    "/{comida_id}",
    status_code=204
)
def eliminar_comida(
    comida_id: int,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    comida = db.query(models.FoodEntry).filter(
        models.FoodEntry.id == comida_id,
        models.FoodEntry.user_id == int(usuario_actual)
    ).first()

    if not comida:
        raise HTTPException(
            status_code=404,
            detail="Comida no encontrada"
        )

    try:
        db.delete(comida)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se pudo eliminar el registro de comida"
        )

    return None
