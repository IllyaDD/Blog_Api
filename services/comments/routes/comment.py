from fastapi import APIRouter, Depends, status, HTTPException, Query
from typing import List, Annotated
from services.comments.query_builder import CommentQueryBuilder, CommentLikeQueryBuilder
from dependecies import session
from dependecies.session import AsyncSessionDep
from models.user import User
from services.comments.schemas import (
    CommentCreateSchema,
    CommentListResponseSchema,
    CommentResponseSchema,
    CommentUpdateSchema,
)
from services.users.modules.manager import current_active_user
from services.comments.errors import CommentNotFound

from common.errors import UnauthorizedAccess
from pydantic import ValidationError
from common.errors import EmptyQueryResult
from common.errors import LikeNotFound
from services.comments.schemas import CommentLikesResponseSchema, CommentLikesListResponseSchema
com_router = APIRouter()


@com_router.delete("/coms/{com_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_com(
    session: AsyncSessionDep, com_id: int, user: User = Depends(current_active_user)
):
    try:
        await CommentQueryBuilder.delete_com(session, com_id, user.id)
    except CommentNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Коментар не знайдено"
        )
    except UnauthorizedAccess:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to change this com",
        )


@com_router.patch("/coms/{com_id}", response_model=CommentResponseSchema)
async def update_com(
    session: AsyncSessionDep,
    com_id: int,
    com_data: CommentUpdateSchema,
    user: User = Depends(current_active_user),
):
    try:
        updated_com = await CommentQueryBuilder.update_com(
            session, com_data, com_id, user.id
        )
        return CommentResponseSchema.model_validate(updated_com)
    except CommentNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Com not found"
        )
    except UnauthorizedAccess:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You cant change this com"
        )


@com_router.get("/coms/my", response_model=CommentListResponseSchema)
async def get_my_coms(
    session: AsyncSessionDep, user: User = Depends(current_active_user)
):
    try:
        return await CommentQueryBuilder.get_com_by_user(session, user.id)
    except EmptyQueryResult:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)


@com_router.get("/post/coms/{post_id}", response_model=CommentListResponseSchema)
async def get_post_coms(
    session: AsyncSessionDep, post_id: int, user: User = Depends(current_active_user)
):
    try:
        return await CommentQueryBuilder.get_post_coms_by_id(session, post_id)
    except EmptyQueryResult:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)


@com_router.post("/coms/likes/{com_id}", status_code=status.HTTP_201_CREATED)
async def like_com(
    session: AsyncSessionDep, com_id: int, user: User = Depends(current_active_user)
):
    try:
        existing_like = await CommentLikeQueryBuilder.get_com_like(
            session, user.id, com_id
        )
        if existing_like:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already liked this comment",
            )
        like = await CommentLikeQueryBuilder.create_like_for_comment(
            session, user.id, com_id
        )
        return {"message": "Liked this post"}
    except CommentNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
@com_router.delete("/coms/likes/{com_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_com(session:AsyncSessionDep, com_id:int, user:User = Depends(current_active_user)):
    try:
        await CommentLikeQueryBuilder.delete_like_from_com(session, com_id, user.id)
        return {'message': "Unliked com"}
    except LikeNotFound:
        raise HTTPException(status_code=status.HTTP_404_NO_CONTENT, detail='Like not found')
    except CommentNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Com not found")
    
    
    
@com_router.get("/coms/likes/my", response_model=CommentLikesListResponseSchema)
async def get_my_comment_likes(
    session: AsyncSessionDep, 
    user: User = Depends(current_active_user)
):
    try:
        likes = await CommentLikeQueryBuilder.get_user_comment_likes(session, user.id)
        
        liked_comments = []
        for like in likes:
            comment = like.comment
            liked_comments.append(CommentLikesResponseSchema(
                id=comment.id,
                content=comment.content,
                author_id=comment.author_id,
                created_at=comment.created_at,
                post_id=comment.post_id,
                parent_id=comment.parent_id,
                number_of_likes=comment.number_of_likes,
                liked_at=like.created_at
            ))
        
        return CommentLikesListResponseSchema(items=liked_comments)
    except EmptyQueryResult:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)