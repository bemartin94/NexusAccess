import uvicorn
from typing import List

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from app.auth.endpoints import router as auth_router_obj
from app.routers.admin_router import router as admin_router_obj
from app.routers.supervisor_router import router as supervisor_router_obj
from app.routers.receptionist_router import router as receptionist_router_obj
from app.visitors.endpoints import router as visitors_router_obj
from app.venues.endpoints import router as venues_router_obj
from app.access.endpoints import router as access_router_obj
from app.id_card_types.endpoints import router as id_card_types_router_obj # <-- Esta importación es la que necesitamos
from app.roles.endpoints import router as roles_router_obj
from app.users.endpoints import router as users_router_obj

# Eliminado: Ya no se necesita IdCardTypeDAL ni IdCardTypeResponse aquí
# from app.id_card_types.dal import IdCardTypeDAL
# from app.id_card_types.schemas import IdCardTypeResponse

app = FastAPI(
    title="NexusAccess API",
    description="API para la gestión de accesos y visitantes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = [
    "http://localhost",
    "http://127.0.0.1:5501",
    "http://127.0.0.1:5500",
    "http://192.168.0.75:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix_base_api = "/app/v1"

app.include_router(auth_router_obj, prefix=f"{prefix_base_api}/auth")
app.include_router(admin_router_obj, prefix=f"{prefix_base_api}/admin")
app.include_router(supervisor_router_obj, prefix=f"{prefix_base_api}/supervisor")
app.include_router(receptionist_router_obj, prefix=f"{prefix_base_api}/receptionist")

app.include_router(users_router_obj, prefix=f"{prefix_base_api}/users")
app.include_router(visitors_router_obj, prefix=f"{prefix_base_api}/visitors")
app.include_router(venues_router_obj, prefix=f"{prefix_base_api}/venues")
app.include_router(access_router_obj, prefix=f"{prefix_base_api}/access")
app.include_router(id_card_types_router_obj, prefix=f"{prefix_base_api}/id_card_types") # <-- Aquí se incluye correctamente
app.include_router(roles_router_obj, prefix=f"{prefix_base_api}/roles")


# Eliminado: El endpoint público de id_card_types se ha movido al router específico si se necesita.
# @app.get(f"{prefix_base_api}/id_card_types", response_model=List[IdCardTypeResponse], tags=["Public"])
# async def get_all_id_card_types_public(db: AsyncSession = Depends(get_db)):
#     id_card_type_dal = IdCardTypeDAL(db)
#     types = await id_card_type_dal.get_id_card_types()
#     return types

@app.get("/")
async def root_message():
    return {"message": "Welcome to NexusAccess API!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
