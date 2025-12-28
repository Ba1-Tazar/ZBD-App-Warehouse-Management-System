from fastapi import APIRouter, HTTPException, Depends, status
from typing import List

# Import modelu bazy danych
from .model import User

# Import schematów Pydantic
from .schemas import UserCreate, UserResponse, UserUpdate

# Import autoryzacji
from .auth import get_current_user, get_admin_user
import bcrypt

# Initialize the router module
router = APIRouter()

# ----------------------------------------------------------------------------------
#                               PUBLIC (NOT LOGGED IN)
# ----------------------------------------------------------------------------------

@router.post("/register", status_code=status.HTTP_201_CREATED, tags=["Users: Public"])
async def register_user(user_data: UserCreate):
    """
    Public registration endpoint.
    """
    if await User.exists(login=user_data.login):
        raise HTTPException(status_code=400, detail="Login already registered")

    hashed = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode()
    await User.create(login=user_data.login, password=hashed, is_admin=False)
    return {"message": "User registered successfully"}

# ----------------------------------------------------------------------------------
#                             USER (LOGGED IN)
# ----------------------------------------------------------------------------------

@router.get("/me", response_model=UserResponse, tags=["Users: User Profile"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated user's profile.
    FastAPI will use UserResponse to filter out the password.
    """
    return current_user


# ----------------------------------------------------------------------------------
#                                  ADMIN ONLY
# ----------------------------------------------------------------------------------

@router.get("/{user_id}", tags=["Users: Admin Management"])
async def get_user_by_id(user_id: int, admin: User = Depends(get_admin_user)):
    """Fetches user details by ID. Restricted to administrators."""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "login": user.login, "is_admin": user.is_admin}

@router.get("/", tags=["Users: Admin Management"])
async def list_users(admin: User = Depends(get_admin_user)):
    """Returns a list of all system users ordered by ID."""
    users = await User.all().order_by("id")
    return [{"id": u.id, "login": u.login, "is_admin": u.is_admin} for u in users]

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users: Admin Management"])
async def create_user(user_data: UserCreate, admin: User = Depends(get_admin_user)):
    """
    Admin tool to manually create users. 
    Uses UserCreate for strict validation (password required).
    """
    if await User.exists(login=user_data.login):
        raise HTTPException(status_code=400, detail="Login already exists")

    hashed = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode()
    
    user = await User.create(
        login=user_data.login, 
        password=hashed, 
        is_admin=user_data.is_admin
    )
    return user

@router.patch("/{user_id}", response_model=UserResponse, tags=["Users: Admin Management"])
async def update_user(user_id: int, user_data: UserUpdate, admin: User = Depends(get_admin_user)): 
    """
    Partial update of user credentials. 
    Only fields provided in the JSON body will be updated.
    """
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data_to_update = user_data.model_dump(exclude_unset=True)

    if "login" in data_to_update:
        new_login = data_to_update["login"]
        if new_login != user.login and await User.exists(login=new_login):
            raise HTTPException(status_code=400, detail="New login is already taken")
        user.login = new_login

    if "password" in data_to_update:
        user.password = bcrypt.hashpw(data_to_update["password"].encode(), bcrypt.gensalt()).decode()
    
    if "is_admin" in data_to_update:
        user.is_admin = data_to_update["is_admin"]
    
    await user.save() 
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users: Admin Management"])
async def delete_user(user_id: int, admin: User = Depends(get_admin_user)):
    """
    Removes a user record. 
    Prevents admins from deleting themselves to maintain system access.
    """
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own admin account")

    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await user.delete() 
    return None # 204 No Content does not return a body
