import asyncio
import asyncpg

# Connect to Database
async def get_connection():
    return await asyncpg.connect(
        user='baltazar',
        password='admin',
        database='myproject',
        host='127.0.0.1'
    )

async def get_user(username: str):
    conn = get_connection()
    user = await conn.fetchrow(
        "SELECT * FROM users WHERE username = $1",
        username
    )
    return user

async def get_users():

    conn = get_connection() 
    rows = await conn.fetch("SELECT * FROM users;")

    return rows

async def add_user(username, email, plain_password):
    conn = get_connection()
    hashed = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()

    await conn.execute(
        "INSERT INTO users (username, email, password_hash) VALUES ($1, $2, $3)",
        username, email, hashed
    )


if __name__ == "__main__":
    
