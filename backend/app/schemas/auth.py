#app.schemas.auth.py 
from pydantic import BaseModel, EmailStr
from typing import Optional
from .enums import CargoEnum

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None
    cargo: Optional[CargoEnum] = None

class TokenRefresh(BaseModel):
    refresh_token: str