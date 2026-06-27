from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import (
    FastAPI,
    HTTPException,
    Depends
)
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

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
    motto = Column(String, nullable=True)


# Create table automatically
Base.metadata.create_all(bind=engine)


# ==========================================
# PASSWORD HASHING
# ==========================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

SECRET_KEY = "super-secret-key-change-this"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


# ==========================================
# DATABASE DEPENDENCY
# ==========================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(data):

    to_encode = data.copy()

    expire = (
        datetime.utcnow()
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update(
        {"exp": expire}
    )

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt
    

def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid token"
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise credentials_exception

    except JWTError:

        raise credentials_exception

    return username


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


class MottoData(BaseModel):

    motto: str


# ==========================================
# REGISTER
# ==========================================

@app.post("/register")
def register(
    user: UserData, 
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if existing_user:
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

    return {
        "message": "Account created successfully"
    }


# ==========================================
# LOGIN
# ==========================================

@app.post("/login")
def login(
    user: UserData, 
    db: Session = Depends(get_db)
    ):


    existing_user = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        user.password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )


    token = create_access_token(
        {
            "sub": existing_user.username
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.post("/save-motto")
def save_motto(
    data: MottoData,
    username: str = Depends(
        get_current_user
    ), 
    db: Session = Depends(get_db)
):
    
    user = (
        db.query(User)
        .filter(
            User.username == username
        )
        .first()
    )

    user.motto = data.motto
    db.commit()
    return {
        "message": "Motto saved"
    }


@app.get("/users")
def get_users(
    db: Session = Depends(get_db)
):

    users = db.query(User).all()
    result = []
    for user in users:
        result.append(
            {
                "username": user.username,
                "motto": user.motto
            }
        )

    return result
# ==========================================
# TEST ROUTE
# ==========================================

@app.get("/")
def root():
    return {
        "message": "FastAPI Authentication Server Running"
    }


@app.get("/me")
def get_me(
    username: str = Depends(
        get_current_user
    )
):

    return {
        "username": username
    }