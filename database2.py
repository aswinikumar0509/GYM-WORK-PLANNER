import os
from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

from logger import log_message

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
default_db_path = BASE_DIR / "fitness1.db"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_db_path}")

print("Using database:", DATABASE_URL)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    age = Column(Integer, nullable=True)
    fitness_level = Column(String, nullable=True)
    goal = Column(String, nullable=True)
    equipment = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)


class WorkoutHistory(Base):
    __tablename__ = "workout_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    workout_plan = Column(Text, nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)
    log_message("Database initialized successfully!")
    print("Tables created and DB initialized.")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(name):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.name == name).first()
        return user
    except Exception as e:
        log_message(f"Error fetching user: {str(e)}", "error")
        return None
    finally:
        session.close()


def add_user(username, email, password_hash, age=None, fitness_level=None, goal=None, equipment=None):
    session = SessionLocal()
    try:
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            log_message(f"User already exists: {username} / {email}", "warning")
            return None

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            age=age,
            fitness_level=fitness_level,
            goal=goal,
            equipment=equipment
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        log_message(f"Added user: {username}")
        return user

    except Exception as e:
        session.rollback()
        log_message(f"Error adding user: {str(e)}", "error")
        return None

    finally:
        session.close()


def get_user_by_username(username):
    session = SessionLocal()
    try:
        return session.query(User).filter(User.username == username).first()

    except Exception as e:
        log_message(f"Error fetching user by username: {str(e)}", "error")
        return None

    finally:
        session.close()


def get_user_by_email(email):
    session = SessionLocal()
    try:
        return session.query(User).filter(User.email == email).first()

    except Exception as e:
        log_message(f"Error fetching user by email: {str(e)}", "error")
        return None

    finally:
        session.close()


def get_user_by_username_or_email(value):
    session = SessionLocal()
    try:
        return session.query(User).filter(
            (User.username == value) | (User.email == value)
        ).first()

    except Exception as e:
        log_message(f"Error fetching user by username/email: {str(e)}", "error")
        return None

    finally:
        session.close()


def save_workout(user_id, workout_plan):
    session = SessionLocal()
    try:
        history = WorkoutHistory(user_id=user_id, workout_plan=workout_plan)
        session.add(history)
        session.commit()
        session.refresh(history)

        log_message(f"Saved workout for user ID: {user_id}")
        return history

    except Exception as e:
        session.rollback()
        log_message(f"Error saving workout: {str(e)}", "error")
        return None

    finally:
        session.close()


if __name__ == "__main__":
    init_db()