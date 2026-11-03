from fastapi import FastAPI
from app.database import engine, Base
from app import models
from app.routers import users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FitLife API")

app.include_router(users.router)


@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a FitLife"}
