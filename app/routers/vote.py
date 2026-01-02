from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status,Query,APIRouter
from sqlmodel import Session
from app.database import get_session
from app.models import VoteCreate,Users,Vote,PostWithVotes,Post
from sqlalchemy import func,select
from .auth import get_current_active_user

SessionDep = Annotated[Session, Depends(get_session)]

router=APIRouter(
    prefix="/votes",
    tags=["Vote"]
)

@router.post("/")
def upvote(payload:VoteCreate,current_user: Annotated[Users, Depends(get_current_active_user)],session:SessionDep):
    vote = session.exec(
        select(Vote).where(
            (Vote.post_id == payload.post_id) &
            (Vote.user_id == current_user.id)
        )
    ).first()

    if vote:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already voted on this post"
        )

    new_vote = Vote(
        post_id=payload.post_id,
        user_id=current_user.id
    )

    session.add(new_vote)
    session.commit()

    return {"message": "Post liked successfully"}


@router.get("/{post_id}", response_model=PostWithVotes)
def get_post_with_votes(
    post_id: int,
    session: SessionDep,
    current_user: Annotated[Users, Depends(get_current_active_user)],
):
    
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    
    stmt = (
    select(
        Post,
        func.count(Vote.user_id).label("vote_count")
    )
    .join(Vote, Vote.post_id == Post.id, isouter=True)
    .where(Post.id == post_id)
    .group_by(Post.id)
)
    row=session.exec(stmt).first()
    _,vote_count = row


    is_voted = session.exec(
        select(Vote)
        .where(
            (Vote.post_id == post_id) &
            (Vote.user_id == current_user.id)
        )
    ).first() is not None

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "vote_count": vote_count,
        "is_voted": is_voted,
    }