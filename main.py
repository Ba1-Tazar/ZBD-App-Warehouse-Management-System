from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from user.controller import router as user_router

# Initialize the main FastAPI application
app = FastAPI(title="User Management API with ORM")

# Register the user routes under the /users path
# Using tags helps group these endpoints in the automatically generated Swagger UI
app.include_router(user_router, prefix="/users", tags=["Users"])

# Tortoise ORM setup and database connection logic
register_tortoise(
    app,
    # Ensure the credentials (user:password@host:port/dbname) match your local Postgres setup
    db_url="postgres://baltazar:admin@127.0.0.1:5432/myproject",
    
    # Define where Tortoise should look for the User models
    modules={"models": ["user.model"]},
    
    # Set to True to automatically create tables on startup if they don't exist
    generate_schemas=True,
    
    # Enable built-in Tortoise handlers to return clean JSON errors on DB failures
    add_exception_handlers=True,
)
