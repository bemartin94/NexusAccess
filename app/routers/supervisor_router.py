# app/routers/supervisor_router.py

from fastapi import APIRouter, Depends
from app.auth.security import has_role, VENUE_SUPERVISOR, SYSTEM_ADMINISTRATOR

# Este router ahora solo define un APIRouter vacío.
# Todas sus funcionalidades se han movido a routers de recursos como app/visitors/endpoints.py y app/access/endpoints.py
router = APIRouter(tags=["Supervisor (Legacy - empty)"], dependencies=[Depends(has_role([VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])

# No hay endpoints definidos aquí, se han movido.
