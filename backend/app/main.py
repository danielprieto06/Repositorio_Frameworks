
from fastapi import FastAPI
from app.database import engine, Base
from app import models
from app.routers import users, exercises, workouts, foods, food_entries, progress
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FitLife API")

app.include_router(users.router)
app.include_router(exercises.router)
app.include_router(workouts.router)
app.include_router(foods.router)
app.include_router(food_entries.router)
app.include_router(progress.router)

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a FitLife"}
