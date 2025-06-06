from fastapi import FastAPI
from app.visitors.endpoints import router as visitors_router
from app.venues.endpoints import router as venues_router
<<<<<<< Updated upstream
=======
from app.access.endpoints import router as access_router
from app.id_card_types.endpoints import router as id_card_types_router
from app.roles.endpoints import router as roles_router
from app.supervisors.endpoints import router as supervisors_router
from app.users.endpoints import router as users_router


>>>>>>> Stashed changes

app = FastAPI()
prefix_base = "/app/v1"

app.include_router(visitors_router, prefix=f"{prefix_base}/visitors")
app.include_router(venues_router, prefix=f"{prefix_base}/venues")
<<<<<<< Updated upstream
=======
app.include_router(access_router, prefix=f"{prefix_base}/access")
app.include_router(id_card_types_router, prefix=f"{prefix_base}/id_card_types")
app.include_router(roles_router, prefix=f"{prefix_base}/roles")
app.include_router(supervisors_router, prefix=f"{prefix_base}/supervisors")
app.include_router(users_router, prefix=f"{prefix_base}/users")




@app.get("/") 
async def hola_mundo(): 
    return {"mensaje": "Hola mundo"} 
>>>>>>> Stashed changes
