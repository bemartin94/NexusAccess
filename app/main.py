from fastapi import FastAPI
from app.visitors.endpoints import router as visitors_router
from app.venues.endpoints import router as venues_router

app = FastAPI()
prefix_base = "/app/v1"

app.include_router(visitors_router, prefix=f"{prefix_base}/visitors")
app.include_router(venues_router, prefix=f"{prefix_base}/venues")
