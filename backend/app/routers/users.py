from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)


@router.get("/", response_model=list[schemas.UserResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.User).all()
    return usuarios
