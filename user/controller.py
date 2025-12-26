from fastapi import APIRouter, HTTPException
from .model import User
from .repository import UserRepository

# Create a router instance for user-related endpoints
router = APIRouter()

# Instantiate the repository to handle database operations
repo = UserRepository()

@router.post("/", status_code=201)
async def create_user(user: User):
    """Creates a new user (POST /users)"""
    await repo.create(user)
    return {"message": "User created successfully"}

@router.get("/{user_id}")
async def get_user_by_id(user_id: int):
    """Retrieves a single user by ID (GET /users/{id})"""
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "login": user.login}

@router.get("/")
async def list_users():
    """Retrieves the list of all users (GET /users)"""
    users = await repo.list()
    return [{"id": u.id, "login": u.login} for u in users]

@router.put("/{user_id}")
async def update_user(user_id: int, user: User): 
    """Updates an existing user (PUT /users/{id})"""
    # Check if user exists
    existing_user = await repo.get(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Use the pydantic object directly
    await repo.update(user_id, user)
    return {"message": "User updated successfully"}

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    """Deletes a user by ID (DELETE /users/{id})"""
    existing_user = await repo.get(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await repo.delete(user_id)
    return {"message": "User deleted successfully"}
