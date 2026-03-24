import os
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from logger import log_message

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
default_db_path = BASE_DIR / "fitness.db"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_db_path}")

print("Using database:", DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    fitness_level = Column(String)
    goal = Column(String)
    equipment = Column(String)


class WorkoutHistory(Base):
    __tablename__ = "workout_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    workout_plan = Column(Text)


def init_db():
    Base.metadata.create_all(bind=engine)
    log_message("✅ Database initialized successfully!")
    print("✅ Tables created and DB initialized.")


def add_user(name, age, fitness_level, goal, equipment):
    session = SessionLocal()
    try:
        user = User(
            name=name,
            age=age,
            fitness_level=fitness_level,
            goal=goal,
            equipment=equipment
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        log_message(f"✅ Added user: {name}")
        return user
    except Exception as e:
        session.rollback()
        log_message(f"❌ Error adding user: {str(e)}", "error")
        return None
    finally:
        session.close()


def get_user(name):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.name == name).first()
        return user
    except Exception as e:
        log_message(f"❌ Error fetching user: {str(e)}", "error")
        return None
    finally:
        session.close()


def save_workout(user_id, workout_plan):
    session = SessionLocal()
    try:
        history = WorkoutHistory(user_id=user_id, workout_plan=workout_plan)
        session.add(history)
        session.commit()
        log_message(f"✅ Saved workout for user ID: {user_id}")
    except Exception as e:
        session.rollback()
        log_message(f"❌ Error saving workout: {str(e)}", "error")
    finally:
        session.close()


if __name__ == "__main__":
    init_db()