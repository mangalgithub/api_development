from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Query,APIRouter
from sqlmodel import Session, select

from app.database import get_session
from app.models import Post,PostUpdate,User
from .auth import get_current_active_user
SessionDep = Annotated[Session, Depends(get_session)]

router=APIRouter(
    prefix="/posts",
    tags=["Post"]
)

@router.post("/",response_model=Post)
def create_post(post: Post, session: SessionDep,current_user: Annotated[User, Depends(get_current_active_user)]):
    post.owner_id=current_user.id;
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@router.get("/", response_model=list[Post])
def read_posts(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    posts = session.exec(
        select(Post)
        .where(Post.owner_id == current_user.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return posts


@router.get("/{post_id}", response_model=Post)
def read_post(post_id: int, session: SessionDep,current_user: Annotated[User, Depends(get_current_active_user)]):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.patch("/{post_id}", response_model=Post)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    post = session.exec(
        select(Post)
        .where((Post.owner_id == current_user.id) & (Post.id==post_id))
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    update_data = post_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(post, field, value)

    session.add(post)
    session.commit()
    session.refresh(post)

    return post

@router.delete("/{post_id}")
def delete_post(post_id: int, session: SessionDep,current_user: Annotated[User, Depends(get_current_active_user)]):
    post = session.exec(
        select(Post)
        .where((Post.owner_id == current_user.id) & (Post.id==post_id))
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    session.delete(post)
    session.commit()
    return {"ok": True}

