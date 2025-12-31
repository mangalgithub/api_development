from typing import Annotated
from fastapi import FastAPI, Depends
from sqlmodel import Session

from app.database import get_session, create_db_and_tables
from .routers import post,user,auth,vote
from fastapi.middleware.cors import CORSMiddleware

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(post.router)
app.include_router(user.router)
app.include_router(vote.router)

# ---------- Startup ----------
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
