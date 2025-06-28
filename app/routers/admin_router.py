# app/routers/admin_router.py

from fastapi import APIRouter, Depends
from app.auth.security import has_role, SYSTEM_ADMINISTRATOR

# Este router ahora solo define un APIRouter vacío.
# Sus funcionalidades se han movido a routers de recursos como app/users/endpoints.py
router = APIRouter(tags=["Admin (Legacy - empty)"], dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])

# No hay endpoints definidos aquí, se han movido.
