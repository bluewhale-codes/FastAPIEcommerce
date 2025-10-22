from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from fastapi import Depends , Request , Response
from sqlalchemy.orm import Session
import hashlib

# -------------------------------------
# Database Config
# -------------------------------------
DATABASE_URL = "mysql+mysqlconnector://root:chandigarhPB%40123@localhost:3306/ecommerce_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# -------------------------------------
# JWT Config
# -------------------------------------
SECRET_KEY = "supersecretkey"  # change this to a long random string
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60




# -------------------------------------
# Password Hashing
# -------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# -------------------------------------
# User Table (SQLAlchemy)
# -------------------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True)
    email = Column(String(100), unique=True)
    password = Column(String(255))

Base.metadata.create_all(bind=engine)

# -------------------------------------
# Pydantic Models
# -------------------------------------
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# -------------------------------------
# Helper Functions
# -------------------------------------
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# -------------------------------------
# FastAPI App
# -------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------
# Register Endpoint
# -------------------------------------

@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Hash password
    hashed_pw = get_password_hash(user.password)

    # Create user
    new_user = User(username=user.username, email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "✅ User registered successfully!"}

# -------------------------------------
# Login Endpoint
# -------------------------------------
@app.post("/login")
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user.username})

    # 🧠 Here is the key line:
    response.set_cookie(
        key="access_token", 
        value=access_token,
        httponly=True,         # 🚫 JS can’t read it
        secure=False,          # True in production (HTTPS only)
        samesite="Lax",        # Helps prevent CSRF
        max_age=1800           # Cookie expiry time
    )

    return {"message": "Login successful"}

# -------------------------------------
# Protected Route (Example)
# -------------------------------------
@app.get("/me")
def read_current_user(request: Request, db: Session = Depends(get_db)):
    # Get token from HttpOnly cookie
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No token found")

    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

       
        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # ✅ Return user details (you can choose which fields to show)
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")