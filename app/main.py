

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse # Para respuestas JSON estándar
from starlette.status import HTTP_404_NOT_FOUND # Para el manejo de 404 si es necesario

# Importa tus routers. Asegúrate de que estas importaciones sean correctas.
from app.auth.endpoints import router as auth_api_router
from app.access.endpoints import router as access_api_router
from app.visitors.endpoints import router as visitors_api_router
# Agrega aquí cualquier otro router que tengas


app = FastAPI(
    title="NexusAccess API",
    description="API para la gestión de accesos",
    version="0.1.0",
)

# Configuración CORS
# Asegúrate que 'http://localhost:5501' es el puerto donde corre tu Live Server (o similar)
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5501", # El puerto de tu frontend (ej. Live Server)
    # Si tu frontend está en otro dominio o puerto, añádelo aquí
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permitir todos los métodos (GET, POST, PUT, DELETE, OPTIONS, PATCH)
    allow_headers=["*"], # Permitir todos los encabezados
)

prefix_base = "/app/v1" # Prefijo base para todas las APIs

# --- INCLUSIÓN DE ROUTERS (¡ESTO ES CLAVE!) ---
# Cada router se incluye con el prefijo base + su propio prefijo de módulo
app.include_router(auth_api_router, prefix=f"{prefix_base}/auth")
app.include_router(access_api_router, prefix=f"{prefix_base}/access") # <-- ESTA ES LA LÍNEA CRÍTICA
app.include_router(visitors_api_router, prefix=f"{prefix_base}/visitors")
# Incluye aquí cualquier otro router de tu aplicación


# Endpoint de prueba para la raíz de la API
@app.get("/")
async def read_root():
    return {"message": "Hola mundo desde NexusAccess API!"}

# Ejemplo de manejo de 404 (opcional, pero útil para depuración)
@app.exception_handler(HTTP_404_NOT_FOUND)
async def custom_404_handler(request, exc):
    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content={"message": "Ruta no encontrada. Por favor, verifica la URL."},
    )

