from fastapi import FastAPI
from db import connect, disconnect
from user import router as user_router

# Initialize the FastAPI application
app = FastAPI(title="User Management API")

# Database connection on startup
@app.on_event("startup")
async def startup_event():
    # Establishes connection to PostgreSQL
    await connect()

# Database disconnection on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    # Safely closes the database connection
    await disconnect()

# Registering user routes
# All endpoints from user/controller.py will now start with /users
app.include_router(user_router, prefix="/users", tags=["users"])
