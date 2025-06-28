# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Importa el router de autenticación principal (renombrado)
from app.auth import endpoints

# Importa los nuevos routers organizados por rol
from app.routers import admin_router, supervisor_router, receptionist_router
from app.visitors.endpoints import router as visitors_router
from app.venues.endpoints import router as venues_router
from app.access.endpoints import router as access_router
from app.id_card_types.endpoints import router as id_card_types_router
from app.roles.endpoints import router as roles_router
from app.users.endpoints import router as users_router
from app.auth.endpoints import router as auth_router


app = FastAPI(
    title="NexusAccess API",
    description="API para la gestión de accesos y visitantes",
    version="1.0.0", # Versión actualizada
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Configuración CORS ---
# Mantén esta configuración CORS igual
origins = [
    "http://localhost",
    "http://127.0.0.1:5501", # Asegúrate de que esta URL sea correcta para tu frontend
    "http://127.0.0.1:5500", # Asegúrate de que esta URL sea correcta para tu frontend
    "http://192.168.0.75:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definimos el prefijo base una sola vez
prefix_base_api = "/app/v1"

# --- Inclusión de Routers (Segun la nueva estructura) ---

# Router de autenticación (solo login /token)
app.include_router(endpoints.router, prefix=f"{prefix_base_api}/auth")

# Routers de alto nivel, organizados por rol, que a su vez incluyen los routers de recursos.
app.include_router(admin_router.router, prefix=f"{prefix_base_api}/admin") # /app/v1/admin/...
app.include_router(supervisor_router.router, prefix=f"{prefix_base_api}/supervisor") # /app/v1/supervisor/...
app.include_router(receptionist_router.router, prefix=f"{prefix_base_api}/receptionist") # /app/v1/receptionist/...
app.include_router(visitors_router, prefix=f"{prefix_base_api}/visitors")
app.include_router(venues_router, prefix=f"{prefix_base_api}/venues")
app.include_router(access_router, prefix=f"{prefix_base_api}/access")
app.include_router(id_card_types_router, prefix=f"{prefix_base_api}/id_card_types")
app.include_router(roles_router, prefix=f"{prefix_base_api}/roles")
app.include_router(users_router, prefix=f"{prefix_base_api}/users")


@app.get("/")
async def root_message(): # Renombrado para mayor claridad
    return {"message": "Welcome to NexusAccess API!"}