from pydantic import BaseModel, EmailStr
from typing import Optional

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    age: Optional[int] = None
    fitness_level: Optional[str] = None
    goal: Optional[str] = None
    equipment: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    age: Optional[int]
    fitness_level: Optional[str]
    goal: Optional[str]
    equipment: Optional[str]
    is_admin: bool