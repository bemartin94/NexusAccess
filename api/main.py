from fastapi import FastAPI
import api.users.endpoints
import api.venues.endpoints

app= FastAPI()
prefix_base= "/api/v1"
app.include_router(api.users.endpoints.router, prefix=f"{prefix_base}/users")
app.include_router(api.venues.endpoints.router, prefix=f"{prefix_base}/endpoints")