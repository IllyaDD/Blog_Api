from fastapi import APIRouter, Depends, status, HTTPException, Query
from typing import List, Annotated
from services.comments.query_builder import CommentQueryBuilder
from dependecies import session
from dependecies.session import AsyncSessionDep
from models import Comment
from models.user import User
from services.comments.schemas import CommentCreateSchema, CommentListResponseSchema, CommentResponseSchema
from services.users.modules.manager import current_active_user

from services.posts.errors import PostNotFound

from pydantic import ValidationError


com_router = APIRouter()


@com_router.post('/coms', status_code=status.HTTP_201_CREATED, response_model=CommentResponseSchema)
async def create_com(
    session:AsyncSessionDep,
    com_data :CommentCreateSchema,
    current_user:User = Depends(current_active_user)
):
    new_com = await CommentQueryBuilder.create_com(
        session,
        com_data=com_data,
        user_id=current_user.id
    )
    return CommentResponseSchema.model_validate(new_com)