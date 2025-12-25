from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException
from db import get_users, get_user, add_user

app = FastAPI()

# --- Pydantic for data validation with POST ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class PasswordChange(BaseModel):
    username: str
    new_password: str

# --- Test Endpoint ---
@app.get("/")
async def home():
    return {"message": "API działa!"}

# Get all users (No password_hash)
@app.get("/users")
async def list_users():
    users = await get_users()
    return [
        {"id": u["id"], "username": u["username"], "email": u["email"]}
        for u in users
    ]

# --- Get one user (No password_hash) ---
@app.get("/users/{username}")
async def get_one_user(username: str):
    user = await get_user(username)
    if user is None:
        return {"error": "User not found"}
    return user

# --- Add new user (POST JSON) ---
@app.post("/users")
async def create_user(user: UserCreate):
    await add_user(user.username, user.email, user.password)
    return {"status": "ok", "username": user.username}

# --- Change user password ---
@app.post("/users/change-password")
async def change_user_password(data: PasswordChange):
    user = await get_user(data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await change_password(data.username, data.new_password)
    return {"status": "ok", "username": data.username, "message": "Password changed"}
