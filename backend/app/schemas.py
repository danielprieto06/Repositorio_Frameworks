
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==============================
# USUARIOS Y AUTENTICACIÓN
# ==============================

# Esquema para iniciar sesión
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Esquema para devolver el token
class Token(BaseModel):
    access_token: str
    token_type: str


# Esquema para crear un usuario
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


# Esquema para mostrar un usuario
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: str


# Esquema para modificar el rol de un usuario
class UserRoleUpdate(BaseModel):
    role: Literal["user", "admin"]


# ==============================
# EJERCICIOS
# ==============================

# Esquema para crear un ejercicio
class ExerciseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=1000)
    muscle_group: str = Field(min_length=1, max_length=50)


# Esquema para mostrar un ejercicio
class ExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    muscle_group: str


# ==============================
# ENTRENAMIENTOS
# ==============================

# Esquema para crear un entrenamiento
class WorkoutCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=1000)


# Esquema para mostrar un entrenamiento
class WorkoutResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    user_id: int


# ==============================
# ALIMENTOS
# ==============================

# Esquema para crear un alimento
class FoodCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    calories: float = Field(ge=0, allow_inf_nan=False)
    protein: float = Field(ge=0, allow_inf_nan=False)
    carbohydrates: float = Field(ge=0, allow_inf_nan=False)
    fats: float = Field(ge=0, allow_inf_nan=False)


# Esquema para mostrar un alimento
class FoodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    calories: float
    protein: float
    carbohydrates: float
    fats: float


# ==============================
# ALIMENTOS CONSUMIDOS
# ==============================

# Esquema para registrar un alimento consumido
class FoodEntryCreate(BaseModel):
    food_id: int = Field(gt=0)
    quantity_g: float = Field(gt=0, allow_inf_nan=False)


# Esquema para mostrar un alimento consumido
class FoodEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    food_id: int
    quantity_g: float
    calories_total: float


# ==============================
# PROGRESO FÍSICO
# ==============================

# Esquema para registrar el progreso físico
class ProgressCreate(BaseModel):
    weight: float = Field(gt=0, allow_inf_nan=False)
    height: float = Field(gt=0, allow_inf_nan=False)


# Esquema para mostrar el progreso físico
class ProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    weight: float
    height: float
    created_at: datetime
    user_id: int
