import bcrypt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from .model import User

security = HTTPBasic()

async def get_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    # Search for the user in the database
    user = await User.get_or_none(login=credentials.username)

    if user:
        # Verify the provided plain-text password against the stored hash
        password_bytes = credentials.password.encode('utf-8')
        hashed_bytes = user.password.encode('utf-8')

        if bcrypt.checkpw(password_bytes, hashed_bytes):
            return user

        # Return unauthorized error if user is missing or password mismatch
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Basic"},
        )

# This function verifies if the authenticated user has admin privileges
async def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation restricted to administrators"
        )
    return current_user
