from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Query,APIRouter
from sqlmodel import Session
from app.database import get_session
from app.models import Users,CreateUser,UserResponse
import bcrypt

SessionDep = Annotated[Session, Depends(get_session)]

router=APIRouter(
    prefix="/users",
    tags=["Users"]
)

def hash_password(password):
    pwd_bytes = password.encode('utf-8') 
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password_bytes.decode('utf-8')

def verify_password(plain_password, hashed_password_from_db):
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_from_db_bytes = hashed_password_from_db.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password_from_db_bytes)



@router.post("/",response_model=UserResponse)
def create_user(payload:CreateUser,session:SessionDep):
    db_user=Users(
        email=payload.email,
        password=hash_password(payload.password)
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user;

@router.get('/{id}',response_model=UserResponse)
def get_user(id:int,session:SessionDep):
    user=session.get(Users,id)
    return user