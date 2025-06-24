from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.visitors.endpoints import router as visitors_router
from app.venues.endpoints import router as venues_router
from app.access.endpoints import router as access_router
from app.id_card_types.endpoints import router as id_card_types_router
from app.roles.endpoints import router as roles_router
from app.supervisors.endpoints import router as supervisors_router
from app.users.endpoints import router as users_router
from app.auth.endpoints import router as auth_router

app = FastAPI(
    title="NexusAccess API",
    description="API para la gestión de accesos",
    version="0.1.0",
)

# --- Configuración CORS ---
# La URL donde se ejecuta tu frontend. Si usas Live Server de VS Code,
# generalmente es http://127.0.0.1:5500 o http://localhost:5500
# Si usas http-server u otro en el puerto 3000, sería http://127.0.0.1:3000
origins = [
    "http://localhost",
    "http://127.0.0.1:5501",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix_base = "/app/v1"

app.include_router(auth_router, prefix="/app/v1/auth")
app.include_router(visitors_router, prefix=f"{prefix_base}/visitors")
app.include_router(venues_router, prefix=f"{prefix_base}/venues")
app.include_router(access_router, prefix=f"{prefix_base}/access")
app.include_router(id_card_types_router, prefix=f"{prefix_base}/id_card_types")
app.include_router(roles_router, prefix=f"{prefix_base}/roles")
app.include_router(supervisors_router, prefix=f"{prefix_base}/supervisors")
app.include_router(users_router, prefix=f"{prefix_base}/users")




@app.get("/") 
async def hola_mundo(): 
    return {"mensaje": "Hola mundo"} 