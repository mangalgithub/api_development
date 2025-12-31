import os 
from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter,Depends,HTTPException,status
from app.models import CreateUser,User
from sqlmodel import Session,select
from app.database import get_session
from typing import Annotated
import bcrypt
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from ..models import Token,TokenData


SessionDep = Annotated[Session, Depends(get_session)]
router=APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def hash_password(password):
    pwd_bytes = password.encode('utf-8') 
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password_bytes.decode('utf-8')

def verify_password(plain_password, hashed_password_from_db):
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_from_db_bytes = hashed_password_from_db.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password_from_db_bytes)

def authenticate_user(user_credentials:User,session:SessionDep):
    user = session.exec(
        select(User).where(User.email == user_credentials.email)
    ).first()
    if not user:
        return False
    if not verify_password(user_credentials.password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(session:SessionDep,token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = session.exec(
        select(User).where(User.email == token_data.email)
    ).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.get("/")
def testing():
    return {"message":"ok"}

@router.post("/login",response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],session:SessionDep):
    user = session.exec(
        select(User).where(User.email == form_data.username)
    ).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer"
    )
    
@router.get("/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
