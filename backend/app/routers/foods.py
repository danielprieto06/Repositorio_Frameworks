
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app import models, schemas
from app.security import require_admin

router = APIRouter(
    prefix="/foods",
    tags=["Nutrición - Alimentos"]
)


# Consultar todos los alimentos
@router.get("/", response_model=list[schemas.FoodResponse])
def listar_alimentos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    alimentos = (
        db.query(models.Food)
        .order_by(models.Food.name)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return alimentos


# Consultar un alimento por su ID
@router.get("/{alimento_id}", response_model=schemas.FoodResponse)
def consultar_alimento(
    alimento_id: int,
    db: Session = Depends(get_db)
):
    alimento = db.query(models.Food).filter(
        models.Food.id == alimento_id
    ).first()

    if not alimento:
        raise HTTPException(
            status_code=404,
            detail="Alimento no encontrado"
        )

    return alimento


# Añadir un alimento
@router.post(
    "/",
    response_model=schemas.FoodResponse,
    status_code=201
)
def crear_alimento(
    datos: schemas.FoodCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.User = Depends(require_admin)
):
    alimento_existente = db.query(models.Food).filter(
        models.Food.name == datos.name
    ).first()

    if alimento_existente:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un alimento con ese nombre"
        )

    nuevo_alimento = models.Food(
        name=datos.name,
        calories=datos.calories,
        protein=datos.protein,
        carbohydrates=datos.carbohydrates,
        fats=datos.fats
    )

    try:
        db.add(nuevo_alimento)
        db.commit()
        db.refresh(nuevo_alimento)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se pudo crear el alimento por un conflicto con los datos"
        )

    return nuevo_alimento


# Modificar un alimento
@router.put(
    "/{alimento_id}",
    response_model=schemas.FoodResponse
)
def modificar_alimento(
    alimento_id: int,
    datos: schemas.FoodCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.User = Depends(require_admin)
):
    alimento = db.query(models.Food).filter(
        models.Food.id == alimento_id
    ).first()

    if not alimento:
        raise HTTPException(
            status_code=404,
            detail="Alimento no encontrado"
        )

    alimento_existente = db.query(models.Food).filter(
        models.Food.name == datos.name,
        models.Food.id != alimento_id
    ).first()

    if alimento_existente:
        raise HTTPException(
            status_code=409,
            detail="Ya existe otro alimento con ese nombre"
        )

    alimento.name = datos.name
    alimento.calories = datos.calories
    alimento.protein = datos.protein
    alimento.carbohydrates = datos.carbohydrates
    alimento.fats = datos.fats

    try:
        db.commit()
        db.refresh(alimento)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se pudo modificar el alimento por un conflicto con los datos"
        )

    return alimento


# Eliminar un alimento
@router.delete(
    "/{alimento_id}",
    status_code=204
)
def eliminar_alimento(
    alimento_id: int,
    db: Session = Depends(get_db),
    usuario_actual: models.User = Depends(require_admin)
):
    alimento = db.query(models.Food).filter(
        models.Food.id == alimento_id
    ).first()

    if not alimento:
        raise HTTPException(
            status_code=404,
            detail="Alimento no encontrado"
        )

    # Comprobar si el alimento está registrado en alguna comida
    alimento_en_uso = db.query(models.FoodEntry).filter(
        models.FoodEntry.food_id == alimento_id
    ).first()

    if alimento_en_uso:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar el alimento porque está siendo utilizado en registros de comidas"
        )

    try:
        db.delete(alimento)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar el alimento porque está relacionado con otros registros"
        )

    return None
