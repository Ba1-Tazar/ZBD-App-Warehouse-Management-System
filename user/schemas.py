from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class UserBase(BaseModel):
    login: str = Field(..., min_length=3, max_length=100, description="Unique username")
    is_admin: bool = Field(default=False, description="Administrative privileges")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Minimum 8 characters")

class UserUpdate(BaseModel):
    login: Optional[str] = Field(None, min_length=3)
    password: Optional[str] = Field(None, min_length=8)
    is_admin: Optional[bool] = None

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "login": "warehouse_worker",
                "is_admin": False
            }
        }
    )
