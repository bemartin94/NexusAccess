# NexusAccess
# NexusAccess: Sistema de Gestión de Acceso de Visitantes

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-orange.svg)
![Pydantic](https://img.shields.io/badge/Pydantic-2.0%2B-brightgreen.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)
![Uvicorn](https://img.shields.io/badge/Server-Uvicorn-blueviolet.svg)

## 🚀 Descripción del Proyecto

## NexusAccess es un sistema robusto y escalable diseñado para la gestión eficiente del acceso de visitantes a múltiples sedes. Permite registrar entradas y salidas, gestionar datos de visitantes, tipos de documentos de identidad, sedes y usuarios internos con diferentes roles.

El objetivo principal es proporcionar una solución integral para el control de acceso, facilitando la auditoría y el seguimiento de las visitas, y mejorando la seguridad en las instalaciones.

 ✨ Características Principales

* **Gestión de Acceso:** Registro de entrada y salida de visitantes con control horario.
* **Gestión de Visitantes:** Registro y actualización de datos de visitantes, incluyendo número y tipo de documento de identidad.
* **Gestión de Sedes (Venues):** Administración de múltiples ubicaciones (sedes) y asignación de supervisores.
* **Gestión de Usuarios:** Roles de usuario (Administrador, Supervisor de Sede, Recepcionista) con permisos diferenciados.
* **API RESTful:** Backend construido con FastAPI para una comunicación eficiente y estructurada.
* **Base de Datos Relacional:** Utiliza SQLAlchemy para la interacción con la base de datos (SQLite por defecto, fácilmente adaptable a PostgreSQL, MySQL, etc.).
* **Validación de Datos:** Pydantic para una validación de datos robusta en los esquemas de entrada y salida.

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3.9+
    * [FastAPI](https://fastapi.tiangolo.com/): Framework web asíncrono para construir APIs.
    * [SQLAlchemy](https://www.sqlalchemy.org/): ORM para la interacción con la base de datos.
    * [Pydantic](https://docs.pydantic.dev/): Librería para la validación de datos con Python type hints.
    * [Uvicorn](https://www.uvicorn.org/): Servidor ASGI para ejecutar la aplicación FastAPI.
    * [Passlib](https://passlib.readthedocs.io/): Para el manejo seguro de contraseñas.
    * [python-jose](https://python-jose.readthedocs.io/): Para JWT (JSON Web Tokens) en la autenticación.
* **Base de Datos:** SQLite (para desarrollo, configurable para producción).

## 🚀 Instalación y Configuración (Para Desarrollo)

Sigue estos pasos para poner en marcha el proyecto en tu entorno local.

1.  **Clona el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/NexusAccess.git](https://github.com/tu-usuario/NexusAccess.git)
    cd NexusAccess
    ```
    *(Reemplaza `tu-usuario` con tu nombre de usuario de GitHub)*

2.  **Crea y activa un entorno virtual:**
    ```bash
    python -m venv .venv
    # En Windows:
    .\.venv\Scripts\activate
    # En macOS/Linux:
    source ./.venv/bin/activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Si no tienes un `requirements.txt`, puedes generarlo con `pip freeze > requirements.txt` después de instalar todas tus dependencias, o simplemente instala las mencionadas en "Tecnologías Utilizadas").*

4.  **Configura las variables de entorno (opcional pero recomendado):**
    Crea un archivo `.env` en la raíz del proyecto y añade las variables de entorno necesarias. Por ejemplo:
    ```
    DATABASE_URL=sqlite:///./database.db
    SECRET_KEY="tu_super_secreta_clave_jwt"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

5.  **Ejecuta las migraciones de la base de datos (o crea las tablas):**
    Si estás usando Alembic para migraciones, ejecuta:
    ```bash
    alembic upgrade head
    ```
    Si no usas Alembic y solo quieres crear las tablas por primera vez (para desarrollo):
    ```python
    # Puedes crear un script Python temporal (e.g., create_db.py)
    # from core.database import Base, engine
    # from core.models import * # Importa todos tus modelos para que Base los detecte
    # Base.metadata.create_all(bind=engine)
    # Luego ejecútalo: python create_db.py
    ```
    *Asegúrate de importar todos tus modelos en `core.models` para que `Base.metadata.create_all` los reconozca.*

6.  **Inicia la aplicación:**
    ```bash
    uvicorn main:app --reload
    ```
    *La API estará disponible en `http://127.0.0.1:8000`.*
    *Puedes acceder a la documentación interactiva de Swagger UI en `http://127.0.0.1:8000/docs`.*

## 🧑‍💻 Uso de la API

La API de NexusAccess expone varios endpoints para interactuar con el sistema. Puedes explorarlos a través de la documentación interactiva (Swagger UI) en `/docs`.

**Endpoints Clave:**
* `/access/`: Gestión de registros de acceso.
* `/visitors/`: Gestión de visitantes.
* `/users/`: Gestión de usuarios internos.
* `/venues/`: Gestión de sedes.
* `/id_card_types/`: Gestión de tipos de documentos de identidad.
* `/auth/token`: Autenticación de usuarios (JWT).

## 📄 Licencia

Este proyecto está bajo la Licencia [MIT](LICENSE).

---
