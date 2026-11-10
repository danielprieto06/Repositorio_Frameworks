
from pydantic import BaseModel
from datetime import datetime

# Esquema para iniciar sesión
class UserLogin(BaseModel):
    email: str
    password: str


# Esquema para devolver el token
class Token(BaseModel):
    access_token: str
    token_type: str


# Esquema para crear un usuario
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


# Esquema para mostrar un usuario
class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


# Esquema para crear un ejercicio
class ExerciseCreate(BaseModel):
    name: str
    description: str
    muscle_group: str


# Esquema para mostrar un ejercicio
class ExerciseResponse(BaseModel):
    id: int
    name: str
    description: str
    muscle_group: str

    class Config:
        from_attributes = True


# Esquema para crear un entrenamiento
class WorkoutCreate(BaseModel):
    title: str
    description: str


# Esquema para mostrar un entrenamiento
class WorkoutResponse(BaseModel):
    id: int
    title: str
    description: str
    user_id: int

    class Config:
        from_attributes = True


# Esquema para crear un alimento
class FoodCreate(BaseModel):
    name: str
    calories: float
    protein: float
    carbohydrates: float
    fats: float


# Esquema para mostrar un alimento
class FoodResponse(BaseModel):
    id: int
    name: str
    calories: float
    protein: float
    carbohydrates: float
    fats: float

    class Config:
        from_attributes = True


# Esquema para registrar un alimento consumido
class FoodEntryCreate(BaseModel):
    food_id: int
    quantity_g: float


# Esquema para mostrar un alimento consumido
class FoodEntryResponse(BaseModel):
    id: int
    user_id: int
    food_id: int
    quantity_g: float
    calories_total: float

    class Config:
        from_attributes = True

# Esquema para registrar el progreso físico
class ProgressCreate(BaseModel):
    weight: float
    height: float


# Esquema para mostrar el progreso físico
class ProgressResponse(BaseModel):
    id: int
    weight: float
    height: float
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True
