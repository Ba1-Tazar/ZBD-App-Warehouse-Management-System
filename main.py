import bcrypt
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from user.controller import router as user_router
from inventory.controller import router as inventory_router
from user.model import User

app = FastAPI(title="Warehouse Management System")
app.include_router(user_router, prefix="/users")
app.include_router(inventory_router, prefix="/inventory")

# Register Tortoise first
register_tortoise(
    app,
    db_url="postgres://baltazar:admin@127.0.0.1:5432/myproject",
    modules={"models": ["user.model", "inventory.model"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

# Startup event: only run AFTER Tortoise is ready
@app.on_event("startup")
async def create_default_admin():
    # This runs after Tortoise is initialized
    admin_exists = await User.filter(login="admin").exists()
    if not admin_exists:
        hashed_password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        await User.create(
            login="admin",
            password=hashed_password,
            is_admin=True
        )
        print("Default admin account initialized.")
    else:
        print("Admin account verification complete.")

