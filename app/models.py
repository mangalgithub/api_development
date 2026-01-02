from sqlmodel import SQLModel, Field,Relationship
from pydantic import EmailStr
from typing import Optional 

class PostUpdate(SQLModel):
    title: str | None = None
    content: str | None = None

class Users(SQLModel,table=True):
    id:int | None=Field(default=None,primary_key=True)
    email:str=Field(unique=True,nullable=False) 
    password:str=Field(nullable=False)

class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    content: str
    owner_id:int | None = Field(default=None, foreign_key="user.id",ondelete="CASCADE")

class CreateUser(SQLModel):
    email:EmailStr
    password:str

class UserResponse(SQLModel):
    email:str
    id:int

class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    email: EmailStr | None = None

class UserInDB(Users):
    hashed_password: str

class Vote(SQLModel,table=True):
    user_id:int | None = Field(default=None,primary_key=True, foreign_key="user.id")
    post_id:int | None = Field(default=None,primary_key=True, foreign_key="post.id")

class VoteCreate(SQLModel):
    post_id:int

class PostWithVotes(SQLModel):
    id: int
    title: str
    content: str
    vote_count: int
    is_voted: bool