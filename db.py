import asyncpg
import bcrypt

# Private global variable to store the active database connection
_connection = None

# Database connection details
DB_CONFIG = {
    "user": "baltazar",
    "password": "admin",
    "database": "myproject",
    "host": "127.0.0.1"
}

async def connect():
    """
    Initializes the database connection using the singleton pattern.
    Stores the connection in the global _connection variable.
    """
    global _connection
    if _connection is None or _connection.is_closed():
        _connection = await asyncpg.connect(**DB_CONFIG)
        print("Database: Connected successfully.")

async def disconnect():
    """
    Closes the database connection if it exists and resets the global variable.
    """
    global _connection
    if _connection:
        await _connection.close()
        _connection = None
        print("Database: Connection closed.")

async def get_connection():
    """
    Returns the active connection object.
    Raises an exception if the connection has not been initialized.
    """
    if _connection is None or _connection.is_closed():
        raise Exception("Database connection not initialized! Call connect() first.")
    return _connection


if __name__ == "__main__":
   pass 
