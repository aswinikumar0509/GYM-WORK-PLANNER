from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import Base, engine, get_db, User
from auth import hash_password, verify_password, create_access_token

app = FastAPI()

Base.metadata.create_all(bind=engine)


class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    age: int | None = None
    fitness_level: str | None = None
    goal: str | None = None
    equipment: str | None = None


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


@app.get("/")
def home():
    return {"message": "Diet Tracker API is running"}


@app.post("/signup")
def signup(user: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        age=user.age,
        fitness_level=user.fitness_level,
        goal=user.goal,
        equipment=user.equipment
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    }


@app.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        (User.username == user.username_or_email) |
        (User.email == user.username_or_email)
    ).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username/email or password")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username/email or password")

    access_token = create_access_token(
        data={
            "sub": db_user.username,
            "email": db_user.email,
            "user_id": db_user.id
        }
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }