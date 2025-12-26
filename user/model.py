from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
    login: str
    password: str

    # clean example for the Swagger UI
    model_config = {
        "json_schema_extra": {
            "example": {
                "login": "admin_user",
                "password": "secret_password"
            }
        }
    }
