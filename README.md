# FitLife – Backend API REST

**Equipo:** VitalTech
**Integrantes:** Daniel y Diego
**Fecha:** Noviembre de 2026

## 1. Descripción del proyecto

FitLife es un proyecto orientado al desarrollo de una aplicación de seguimiento de la actividad física, los entrenamientos, la alimentación y el progreso personal de los usuarios.

Esta primera entrega se centra en el desarrollo del backend y de una API REST que permite gestionar la información de la aplicación y comunicarse con una futura aplicación móvil desarrollada con Flutter.

El backend está desarrollado con FastAPI y utiliza PostgreSQL como sistema de gestión de bases de datos.

## 2. Tecnologías utilizadas

- **Python:** lenguaje de programación.
- **FastAPI:** framework para el desarrollo de la API REST.
- **PostgreSQL 16:** sistema de gestión de bases de datos.
- **SQLAlchemy:** ORM para la comunicación con la base de datos.
- **Alembic:** herramienta para gestionar las migraciones.
- **Pydantic:** validación de datos.
- **PyJWT:** gestión de tokens JWT.
- **Docker Compose:** ejecución del servicio PostgreSQL.
- **Pytest:** pruebas automatizadas.
- **HTTPX:** cliente utilizado para probar la API.

## 3. Estructura del proyecto

La estructura principal del repositorio es la siguiente:

```text
Repositorio_Frameworks/
│
├── README.md
│
└── backend/
    │
    ├── alembic/
    │   ├── versions/
    │   │   ├── 197ea14ce284_baseline_inicial_fitlife.py
    │   │   └── 443ca17f7983_añadir_rol_a_usuarios.py
    │   │
    │   ├── env.py
    │   ├── README
    │   └── script.py.mako
    │
    ├── app/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── database.py
    │   ├── main.py
    │   ├── models.py
    │   ├── schemas.py
    │   ├── security.py
    │   │
    │   └── routers/
    │       ├── __init__.py
    │       ├── exercises.py
    │       ├── food_entries.py
    │       ├── foods.py
    │       ├── progress.py
    │       ├── users.py
    │       └── workouts.py
    │
    ├── tests/
    │   └── test_main.py
    │
    ├── .env.example
    ├── .gitignore
    ├── alembic.ini
    ├── docker-compose.yml
    └── requirements.txt
```

## 4. Funcionalidades principales

El backend contempla los siguientes módulos:

- **Usuarios:** registro, inicio de sesión, consulta del perfil y gestión de roles.
- **Ejercicios:** consulta y gestión del catálogo de ejercicios.
- **Entrenamientos:** gestión de entrenamientos asociados a cada usuario.
- **Alimentos:** gestión del catálogo de alimentos.
- **Registros alimentarios:** registro de alimentos consumidos, cálculo de calorías y resumen diario.
- **Progreso:** seguimiento de datos personales como peso, altura e IMC.

Las operaciones protegidas requieren autenticación y respetan los permisos correspondientes.

## 5. Requisitos previos

Para instalar y ejecutar el proyecto se necesita:

- Python 3.14.4.
- PostgreSQL 16, ejecutado mediante Docker Compose.
- Docker y Docker Compose.
- Git.
- Un entorno virtual de Python.

## 6. Instalación y configuración

Clonar el repositorio:

```bash
git clone https://github.com/danielprieto06/Repositorio_Frameworks.git
```

Acceder a la carpeta del proyecto:

```bash
cd Repositorio_Frameworks/backend
```

Crear el entorno virtual:

```bash
python -m venv .venv
```

Activarlo en Linux:

```bash
source .venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Crear el archivo de configuración a partir del ejemplo:

```bash
cp .env.example .env
```

Configurar las siguientes variables en el archivo `.env`:

- `DATABASE_URL`: dirección de conexión a PostgreSQL.
- `SECRET_KEY`: clave secreta utilizada para firmar los tokens JWT.
- `CORS_ORIGINS`: lista de orígenes autorizados para las peticiones del frontend.

No se deben subir al repositorio las claves secretas ni el archivo `.env`.

## 7. Base de datos

El proyecto utiliza PostgreSQL 16 mediante Docker Compose.

Desde la carpeta `backend`, iniciar el servicio:

```bash
docker compose up -d
```

Comprobar que el contenedor está funcionando:

```bash
docker compose ps
```

La configuración de Docker Compose utiliza:

- **Servicio:** db.
- **Base de datos:** fitlife.
- **Usuario:** fitlife.
- **Puerto:** 5432.

La conexión de la aplicación se configura mediante la variable `DATABASE_URL`.

## 8. Migraciones con Alembic

Alembic permite gestionar los cambios de estructura de la base de datos.

Consultar la revisión actual:

```bash
alembic current
```

Consultar el historial de migraciones:

```bash
alembic history
```

Aplicar todas las migraciones pendientes:

```bash
alembic upgrade head
```

El proyecto dispone de dos migraciones:

1. Migración inicial con la estructura principal de las tablas.
2. Migración para incorporar el campo de rol de los usuarios, con valor predeterminado `user`.

## 9. Creación del primer administrador

Después de registrar un usuario mediante la API, se puede asignar manualmente el rol de administrador a su cuenta.

Desde la carpeta `backend`, ejecutar el siguiente comando, sustituyendo el correo por el del usuario registrado:

```bash
docker compose exec db psql -U fitlife -d fitlife -c "UPDATE users SET role='admin' WHERE email='tu@correo.com';"
```

Una vez creado el primer administrador, este podrá gestionar los roles de otros usuarios mediante la ruta protegida correspondiente.

La gestión de roles se realiza mediante:

```text
PATCH /users/admin/users/{user_id}/role
```

## 10. Ejecución del backend

Desde la carpeta `backend`, con el entorno virtual activado:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:

```text
http://127.0.0.1:8000
```

Para detener el servidor, utilizar `Ctrl + C` en la terminal.

## 11. Documentación de la API

FastAPI genera automáticamente documentación interactiva mediante Swagger UI.

Acceso a Swagger:

```text
http://127.0.0.1:8000/docs
```

Documentación alternativa:

```text
http://127.0.0.1:8000/redoc
```

Desde Swagger se pueden consultar y probar las rutas, registrar usuarios, iniciar sesión y utilizar los tokens JWT para acceder a los endpoints protegidos.

## 12. Seguridad y autenticación

El backend incorpora diferentes mecanismos de seguridad:

### 12.1. Protección de contraseñas

Las contraseñas se almacenan mediante hash PBKDF2-HMAC-SHA256.

Se utiliza:

- Salt aleatorio de 16 bytes.
- 600.000 iteraciones.
- Comparación segura mediante `secrets.compare_digest`.

Las contraseñas originales no se almacenan en la base de datos.

### 12.2. Autenticación JWT

La autenticación utiliza tokens JWT firmados mediante HS256.

Los tokens incluyen:

- Identificador del usuario en el campo `sub`.
- Tiempo de expiración de 30 minutos.

Las rutas protegidas utilizan el encabezado:

```text
Authorization: Bearer <token>
```

### 12.3. Roles y permisos

El sistema contempla dos roles:

- `user`: usuario estándar.
- `admin`: administrador.

Las operaciones administrativas requieren los permisos correspondientes.

Se utilizan dependencias como `get_current_user` y `require_admin` para proteger las rutas.

### 12.4. Códigos de respuesta de seguridad

Entre los códigos HTTP utilizados se encuentran:

- `401 Unauthorized`: falta autenticación válida.
- `403 Forbidden`: el usuario no dispone de permisos suficientes.
- `404 Not Found`: recurso no encontrado.
- `422 Unprocessable Entity`: datos de entrada no válidos.
- `409 Conflict`: conflicto de integridad en la base de datos.

## 13. Middleware y gestión de errores

La aplicación incorpora los siguientes middleware y mecanismos:

- **CORSMiddleware:** permite controlar los orígenes autorizados para las peticiones.
- **GZipMiddleware:** comprime respuestas superiores a 1.000 bytes.
- **Middleware personalizado:** mide el tiempo de procesamiento y devuelve la cabecera `X-Process-Time`.
- **Gestión de IntegrityError:** transforma determinados conflictos de integridad de la base de datos en respuestas HTTP 409.

Estos mecanismos ayudan a mejorar la comunicación entre el cliente y el backend y a gestionar errores de forma controlada.

## 14. Pruebas automatizadas

El proyecto incluye pruebas automatizadas desarrolladas con Pytest y HTTPX.

Para ejecutar las pruebas, situarse en la carpeta `backend` y activar el entorno virtual:

```bash
python -m pytest -v
```

Las cinco pruebas implementadas verifican:

1. El funcionamiento de la ruta inicial.
2. La cabecera de tiempo de procesamiento `X-Process-Time`.
3. La respuesta CORS preflight.
4. La protección de una ruta sin token de autenticación.
5. La validación de datos incorrectos durante el registro.

**Resultado de la última ejecución: 5 pruebas superadas.**

## 15. Control de versiones

El proyecto utiliza Git y GitHub para el control de versiones y el trabajo colaborativo.

Los cambios se gestionan mediante commits y sincronización con el repositorio remoto.

## 16. Estado de la entrega

Esta primera entrega se centra en el backend y en la API REST de FitLife.

Se han implementado los módulos principales, la conexión con PostgreSQL, las migraciones, la autenticación, los permisos, los middleware y las pruebas automatizadas.

La aplicación móvil desarrollada con Flutter queda prevista para una fase posterior del proyecto.

## 17. Equipo de desarrollo

**Equipo:** VitalTech

**Integrantes:**
- Daniel.
- Diego.

**Proyecto:** FitLife.

**Entrega:** Primera fase – Backend y API REST.

**Fecha:** Noviembre de 2026.
