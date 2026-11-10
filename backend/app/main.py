import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.routers import users, exercises, workouts, foods, food_entries, progress


app = FastAPI(title="FitLife API")


# 1. CORS: permite las peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# 2. GZip: comprime respuestas de más de 1000 bytes
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)


# 3. Middleware personalizado: mide el tiempo de cada petición
@app.middleware("http")
async def medir_tiempo_peticion(request: Request, call_next):
    inicio = time.perf_counter()

    response = await call_next(request)

    duracion = time.perf_counter() - inicio
    response.headers["X-Process-Time"] = str(duracion)

    print(
        f"{request.method} {request.url.path} "
        f"- Estado: {response.status_code} "
        f"- Tiempo: {duracion:.4f}s"
    )

    return response


# 4. Manejo global de errores de integridad de la base de datos
@app.exception_handler(IntegrityError)
async def manejar_error_integridad(
    request: Request,
    exc: IntegrityError
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Conflicto con los datos existentes en la base de datos."
        },
    )


# Rutas de la API
app.include_router(users.router)
app.include_router(exercises.router)
app.include_router(workouts.router)
app.include_router(foods.router)
app.include_router(food_entries.router)
app.include_router(progress.router)


@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a FitLife"}
