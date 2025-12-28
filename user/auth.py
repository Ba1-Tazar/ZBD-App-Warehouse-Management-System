import bcrypt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from .model import User

security = HTTPBasic()

async def get_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    """
    Authenticates the user using HTTP Basic Auth.
    Verifies credentials against the database and bcrypt hashes.
    """
    # 1. Fetch user from database
    user = await User.get_or_none(login=credentials.username)

    # 2. Check if user exists and verify password
    if user:
        password_bytes = credentials.password.encode('utf-8')
        hashed_bytes = user.password.encode('utf-8')

        if bcrypt.checkpw(password_bytes, hashed_bytes):
            return user

    # 3. Raise 401 if EITHER user is missing OR password is wrong
    # Note: This must be OUTSIDE the 'if user' block to catch missing users
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect login or password",
        headers={"WWW-Authenticate": "Basic"},
    )

async def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    Authorization layer: Checks if the authenticated user has admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation restricted to administrators"
        )
    return current_user
