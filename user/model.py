from tortoise import fields, models
from pydantic import BaseModel
from typing import Optional

# Tortoise ORM Model: Defines the database schema and table structure
class User(models.Model):
    # Primary key with auto-increment
    id = fields.IntField(pk=True)
    # Unique login string to prevent duplicate accounts
    login = fields.CharField(max_length=100, unique=True)
    # Stores the hashed password string
    password = fields.CharField(max_length=255)

    class Meta:
        # Explicitly naming the table in PostgreSQL
        table = "users"

# Pydantic Model: Defines data validation rules for incoming API requests
class UserSchema(BaseModel):
    # ID is optional because it is not required when creating a new user
    id: Optional[int] = None
    login: str
    password: str

    # Configuration for how this model appears in the Swagger/OpenAPI docs
    model_config = {
        "json_schema_extra": {
            "example": {
                "login": "admin_user",
                "password": "secret_password"
            }
        }
    }
