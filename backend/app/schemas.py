from pydantic import BaseModel


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
    user_id: int


# Esquema para mostrar un entrenamiento
class WorkoutResponse(BaseModel):
    id: int
    title: str
    description: str
    user_id: int

    class Config:
        from_attributes = True
