from fastapi import APIRouter, HTTPException
from .model import User, UserSchema 
import bcrypt

# Initialize the router module
router = APIRouter()

@router.post("/", status_code=201)
async def create_user(user_data: UserSchema):
    """Handles new user registration and password hashing"""
    # Hash the plain-text password before storing it for security
    hashed = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode() 
    
    # Persist the new user record to the database
    await User.create(login=user_data.login, password=hashed)
    return {"message": "User created successfully"}

@router.get("/{user_id}")
async def get_user_by_id(user_id: int):
    """Fetches a specific user by their unique ID"""
    user = await User.get_or_none(id=user_id)
    
    # Return a 404 error if the user does not exist in the database
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"id": user.id, "login": user.login}

@router.get("/")
async def list_users():
    """Returns a list of all registered users"""
    users = await User.all().order_by("id")
    # Serialize the ORM objects into a simple list of dictionaries
    return [{"id": u.id, "login": u.login} for u in users]

@router.put("/{user_id}")
async def update_user(user_id: int, user_data: UserSchema): 
    """Updates user credentials for an existing record"""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Re-hash the new password and update the model instance
    hashed = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode()
    user.login = user_data.login
    user.password = hashed
    
    # Commit changes to the database
    await user.save() 
    return {"message": "User updated successfully"}

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    """Removes a user record from the system"""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Execute the deletion query
    await user.delete() 
    return {"message": "User deleted successfully"}
