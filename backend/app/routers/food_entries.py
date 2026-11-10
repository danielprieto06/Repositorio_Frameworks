
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.database import get_db
from app import models, schemas
from app.security import get_current_user

router = APIRouter(
    prefix="/food-entries",
    tags=["Nutrición - Registro de comidas"]
)


# Consultar las comidas del usuario
@router.get("/", response_model=list[schemas.FoodEntryResponse])
def listar_comidas(
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    comidas = db.query(models.FoodEntry).filter(
        models.FoodEntry.user_id == int(usuario_actual)
    ).all()

    return comidas


# Consultar el resumen diario de calorías
@router.get("/daily-summary")
def resumen_diario(
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    hoy = datetime.utcnow().date()

    total_calorias = db.query(
        func.coalesce(func.sum(models.FoodEntry.calories_total), 0)
    ).filter(
        models.FoodEntry.user_id == int(usuario_actual),
        func.date(models.FoodEntry.consumed_at) == hoy
    ).scalar()

    return {
        "fecha": str(hoy),
        "calorias_consumidas": round(float(total_calorias), 2)
    }


# Consultar una comida por su ID
@router.get("/{comida_id}", response_model=schemas.FoodEntryResponse)
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
@router.post("/", response_model=schemas.FoodEntryResponse)
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

    if datos.quantity_g <= 0:
        raise HTTPException(
            status_code=400,
            detail="La cantidad debe ser mayor que cero"
        )

    calorias = alimento.calories * datos.quantity_g / 100

    nueva_comida = models.FoodEntry(
        user_id=int(usuario_actual),
        food_id=datos.food_id,
        quantity_g=datos.quantity_g,
        calories_total=calorias
    )

    db.add(nueva_comida)
    db.commit()
    db.refresh(nueva_comida)

    return nueva_comida


# Modificar la cantidad de una comida
@router.put("/{comida_id}", response_model=schemas.FoodEntryResponse)
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

    if datos.quantity_g <= 0:
        raise HTTPException(
            status_code=400,
            detail="La cantidad debe ser mayor que cero"
        )

    comida.food_id = datos.food_id
    comida.quantity_g = datos.quantity_g
    comida.calories_total = alimento.calories * datos.quantity_g / 100

    db.commit()
    db.refresh(comida)

    return comida


# Eliminar una comida
@router.delete("/{comida_id}")
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

    db.delete(comida)
    db.commit()

    return {"mensaje": "Comida eliminada correctamente"}
