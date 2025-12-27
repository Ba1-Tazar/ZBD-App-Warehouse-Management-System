from fastapi import APIRouter, HTTPException, Depends
from .model import User, UserSchema 
from .auth import get_current_user, get_admin_user
import bcrypt

# Initialize the router module
router = APIRouter()

# ----------------------------------------------------------------------------------
#                               PUBLIC
# ----------------------------------------------------------------------------------

@router.post("/register", status_code=201)
async def register_user(user_data: UserSchema):
    """
    Public endpoint for new user registration.
    No authentication dependency here so anyone can create an account.
    """
    # Check if the login is already taken to provide a clean error message
    existing_user = await User.get_or_none(login=user_data.login)
    if existing_user:
        raise HTTPException(status_code=400, detail="Login already registered")

    # Hash the password before saving for security
    hashed = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode()
    
    # Create the user record in the database
    await User.create(login=user_data.login, password=hashed)
    return {"message": "User registered successfully"}

# ----------------------------------------------------------------------------------
#                           LOGGED-IN USER ONLY
# ----------------------------------------------------------------------------------

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Private endpoint: Requires authentication via HTTP Basic.
    """
    return {"id": current_user.id, "login": current_user.login}


# ----------------------------------------------------------------------------------
#                               ADMIN ONLY
# ----------------------------------------------------------------------------------

@router.get("/{user_id}")
async def get_user_by_id(user_id: int, current_user: User = Depends(get_admin_user)):
    """Fetches a specific user by their unique ID"""
    user = await User.get_or_none(id=user_id)
    
    # Return a 404 error if the user does not exist in the database
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"id": user.id, "login": user.login}

@router.get("/")
async def list_users(current_user: User = Depends(get_admin_user)):
    """Returns a list of all registered users"""

    users = await User.all().order_by("id")
    return [{"id": u.id, "login": u.login} for u in users]

@router.post("/", status_code=201)
async def create_user(user_data: UserSchema, current_user: User = Depends(get_admin_user)):
    """Handles new user registration and password hashing"""
    # Hash the plain-text password before storing it for security
    hashed = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode() 
    
    # Persist the new user record to the database
    await User.create(login=user_data.login, password=hashed)
    return {"message": "User created successfully"}

@router.put("/{user_id}")
async def update_user(user_id: int, user_data: UserSchema, current_user: User = Depends(get_admin_user)): 
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
async def delete_user(user_id: int, current_user: User = Depends(get_admin_user)):
    """Removes a user record from the system"""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Execute the deletion query
    await user.delete() 
    return {"message": "User deleted successfully"}
