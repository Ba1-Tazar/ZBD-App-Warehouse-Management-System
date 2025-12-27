import bcrypt
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from user.controller import router as user_router
from inventory.controller import router as inventory_router
from user.model import User

app = FastAPI(title="Warehouse Management System")

app.include_router(user_router, prefix="/users")
app.include_router(inventory_router, prefix="/inventory")

async def create_default_admin():
    # Ensure the system has at least one administrative account on startup
    admin_exists = await User.filter(login="admin").exists()
    
    if not admin_exists:
        # Generate hash for the default credentials
        hashed_password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        
        await User.create(
            login="admin",
            password=hashed_password,
            is_admin=True
        )
        print("Default admin account initialized.")
    else:
        print("Admin account verification complete.")

register_tortoise(
    app,
    db_url="postgres://baltazar:admin@127.0.0.1:5432/myproject",
    modules={"models": ["user.model"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.on_event("startup")
async def startup_event():
    # Run database seeding routines
    await create_default_admin()
