# FitLife

FitLife es una aplicación orientada al seguimiento de la actividad física, los entrenamientos, la alimentación y el progreso personal.

FitLife contempla una aplicación móvil prevista con Flutter y un backend implementado como API REST con FastAPI. En esta primera entrega se presenta el backend; la aplicación móvil se desarrollará en una fase posterior.
## 1. Tecnologías utilizadas

### Aplicación móvil (fase futura)
- Flutter 3.x
- Dart 3.x
- Android Studio 2025.1 o superior

### Backend
- Python 3.14.4
- FastAPI 0.115.x
- Uvicorn 0.30.x
- SQLAlchemy
- Pydantic

### Base de datos
- PostgreSQL 16
- Docker y Docker Compose
- Alembic para las migraciones

### Herramientas
- Visual Studio Code 1.139.0
- Postman 11.x
- Swagger UI
- Git y GitHub

## 2. Estructura del backend

```text
backend/
├── alembic/
│   └── versions/
├── app/
│   ├── routers/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── security.py
├── .env.example
├── alembic.ini
├── docker-compose.yml
└── requirements.txt
```

## 3. Requisitos previos

Para ejecutar el backend se necesita:

- Python 3.14.4
- Docker y Docker Compose
- pip

## 4. Instalación y configuración

Clonar el repositorio:

```bash
git clone https://github.com/danielprieto06/Repositorio_Frameworks.git
cd Repositorio_Frameworks/backend
```

Crear un entorno virtual:

```bash
python3 -m venv .venv
```

Activarlo en Linux:

```bash
source .venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Crear el archivo `.env` a partir del ejemplo:

```bash
cp .env.example .env
```

Configurar en `.env` las variables necesarias:

- `DATABASE_URL`: dirección de conexión a PostgreSQL.
- `SECRET_KEY`: clave secreta utilizada para firmar los tokens JWT.
- `CORS_ORIGINS`: orígenes autorizados para las peticiones desde el frontend.

No se deben subir al repositorio las claves secretas ni el archivo `.env`.

## 5. Base de datos

Desde la carpeta `backend`, iniciar PostgreSQL mediante Docker Compose:

```bash
docker compose up -d
```

Comprobar que el contenedor está funcionando:

```bash
docker compose ps
```

## 6. Migraciones

Para consultar la revisión actual:

```bash
alembic current
```

Para aplicar las migraciones pendientes:

```bash
alembic upgrade head
```

## 7. Ejecutar el backend

Desde la carpeta `backend`, con el entorno virtual activado:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:

http://127.0.0.1:8000

## 8. Documentación de la API

FastAPI genera automáticamente la documentación interactiva mediante Swagger UI:

http://127.0.0.1:8000/docs

También se puede consultar la documentación alternativa en:

http://127.0.0.1:8000/redoc

Desde Swagger se pueden probar las rutas, registrar usuarios, iniciar sesión y utilizar los tokens JWT para acceder a los endpoints protegidos.

## 9. Seguridad

La API incorpora:

- Autenticación mediante tokens JWT.
- Contraseñas almacenadas mediante hash PBKDF2 con SHA-256 y salt.
- Protección de rutas mediante dependencias de autenticación.
- Control de permisos para operaciones de administrador.
- Validación de datos mediante Pydantic.
- Gestión de conflictos de integridad de la base de datos.

## 10. Pruebas

Para ejecutar las pruebas automatizadas, si están disponibles:

```bash
pytest
```

## 11. Control de versiones

El proyecto utiliza Git y GitHub para el control de versiones y el trabajo colaborativo.
