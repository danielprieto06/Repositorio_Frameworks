
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import get_current_user

router = APIRouter(prefix="/foods", tags=["Nutrición - Alimentos"])


# Consultar todos los alimentos
@router.get("/", response_model=list[schemas.FoodResponse])
def listar_alimentos(db: Session = Depends(get_db)):
    alimentos = db.query(models.Food).all()
    return alimentos


# Consultar un alimento por su ID
@router.get("/{alimento_id}", response_model=schemas.FoodResponse)
def consultar_alimento(alimento_id: int, db: Session = Depends(get_db)):
    alimento = db.query(models.Food).filter(
        models.Food.id == alimento_id
    ).first()

    if not alimento:
        raise HTTPException(status_code=404, detail="Alimento no encontrado")

    return alimento


# Añadir un alimento
@router.post("/", response_model=schemas.FoodResponse)
def crear_alimento(
    datos: schemas.FoodCreate,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    alimento_existente = db.query(models.Food).filter(
        models.Food.name == datos.name
    ).first()

    if alimento_existente:
        raise HTTPException(status_code=400, detail="El alimento ya existe")

    nuevo_alimento = models.Food(
        name=datos.name,
        calories=datos.calories,
        protein=datos.protein,
        carbohydrates=datos.carbohydrates,
        fats=datos.fats
    )

    db.add(nuevo_alimento)
    db.commit()
    db.refresh(nuevo_alimento)

    return nuevo_alimento


# Modificar un alimento
@router.put("/{alimento_id}", response_model=schemas.FoodResponse)
def modificar_alimento(
    alimento_id: int,
    datos: schemas.FoodCreate,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    alimento = db.query(models.Food).filter(
        models.Food.id == alimento_id
    ).first()

    if not alimento:
        raise HTTPException(status_code=404, detail="Alimento no encontrado")

    alimento.name = datos.name
    alimento.calories = datos.calories
    alimento.protein = datos.protein
    alimento.carbohydrates = datos.carbohydrates
    alimento.fats = datos.fats

    db.commit()
    db.refresh(alimento)

    return alimento


# Eliminar un alimento
@router.delete("/{alimento_id}")
def eliminar_alimento(
    alimento_id: int,
    db: Session = Depends(get_db),
    usuario_actual: str = Depends(get_current_user)
):
    alimento = db.query(models.Food).filter(
        models.Food.id == alimento_id
    ).first()

    if not alimento:
        raise HTTPException(status_code=404, detail="Alimento no encontrado")

    db.delete(alimento)
    db.commit()

    return {"mensaje": "Alimento eliminado correctamente"}
