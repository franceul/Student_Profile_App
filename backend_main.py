from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from passlib.context import CryptContext

# ==========================================
# DATABASE SETUP
# ==========================================

DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ==========================================
# USER TABLE
# ==========================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)


# Create table automatically
Base.metadata.create_all(bind=engine)


# ==========================================
# PASSWORD HASHING
# ==========================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # okay for learning
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# REQUEST MODEL
# ==========================================

class UserData(BaseModel):
    username: str
    password: str


# ==========================================
# REGISTER
# ==========================================

@app.post("/register")
def register(user: UserData):

    db = SessionLocal()

    existing_user = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if existing_user:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    new_user = User(
        username=user.username,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()

    db.close()

    return {
        "message": "Account created successfully"
    }


# ==========================================
# LOGIN
# ==========================================

@app.post("/login")
def login(user: UserData):

    db = SessionLocal()

    existing_user = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if not existing_user:
        db.close()
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        user.password,
        existing_user.hashed_password
    ):
        db.close()
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    db.close()

    return {
        "message": "Login successful"
    }


# ==========================================
# TEST ROUTE
# ==========================================

@app.get("/")
def root():
    return {
        "message": "FastAPI Authentication Server Running"
    }