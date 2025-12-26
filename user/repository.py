from db import get_connection
from .model import User
import bcrypt

class UserRepository:

   # 1. Fetch all users and return them as a list of User objects
    async def list(self):
        conn = await get_connection()
        rows = await conn.fetch("SELECT id, username, password_hash FROM users")
        # Mapping database rows to User class instances
        return [User(id=row['id'], login=row['username'], password=row['password_hash']) for row in rows]

    # 2. Get a single user by their numeric ID
    async def get(self, user_id: int):
        conn = await get_connection()
        row = await conn.fetchrow("SELECT id, username, password_hash FROM users WHERE id = $1", user_id)
        if row:
            return User(id=row['id'], login=row['username'], password=row['password_hash'])
        return None

    # 3. Create a new user from a User object 
    async def create(self, user: User):
        conn = await get_connection()
        # Hash the password before saving for security
        hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
        await conn.execute(
            "INSERT INTO users (username, password_hash) VALUES ($1, $2)",
            user.login, hashed
        )

    # 4. Update an existing user's data 
    async def update(self, user_id: int, user: User):
        conn = await get_connection()
        hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
        await conn.execute(
            "UPDATE users SET username=$1, password_hash=$2 WHERE id=$3",
            user.login, hashed, user_id
        )

    # 5. Remove a user from the database
    async def delete(self, user_id: int):
        conn = await get_connection()
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)
