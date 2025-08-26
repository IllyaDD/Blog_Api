from fastapi import APIRouter, Depends, status, HTTPException, Query
from typing import List, Annotated

from dependecies import session
from dependecies.session import AsyncSessionDep
from models import Post, post
from models.user import User
from services.posts.schemas import (
    PostCreateSchema,
    PostListResponseSchema,
    PostResponseSchema,
    PostUpdateSchema,
)
from common.schemas import PaginationParams
from services.posts.schemas.filters import PostFilter
from services.posts.query_builder import PostQueryBuilder
from common import EmptyQueryResult
from services.users.modules.manager import current_active_user

from services.posts.errors import PostNotFound
from common.errors import UnauthorizedAccess
from pydantic import ValidationError


post_router = APIRouter()


@post_router.get("/posts", response_model=PostListResponseSchema)
async def get_posts(
    session: AsyncSessionDep,
    current_user: Annotated[User, Depends(current_active_user)],
    pagination_params: Annotated[PaginationParams, Depends()],
    post_name: str = Query(None, description="Find post by title"),
    post_content: str = Query(None, description="Find post by content"),
    author_id: int = Query(None, description="Filter by author ID"),
    is_published: bool = Query(
        None, description="Filter your posts by publication status"
    ),
):
    try:

        if is_published is False and author_id is None:
            author_id = current_user.id

        if post_name is not None:
            posts = await PostQueryBuilder.get_post_by_name(session, post_name)
            post_schemas = [PostResponseSchema.model_validate(post) for post in posts]
            return PostListResponseSchema(items=post_schemas)

        if post_content is not None:
            posts = await PostQueryBuilder.get_post_by_content(session, post_content)
            post_schemas = [PostResponseSchema.model_validate(post) for post in posts]
            return PostListResponseSchema(items=post_schemas)

        filters = PostFilter(
            title=post_name, author_id=author_id, is_published=is_published
        )

        posts = await PostQueryBuilder.get_posts_pagination(
            session, pagination_params, filters
        )

        post_schemas = [PostResponseSchema.model_validate(post) for post in posts]
        return PostListResponseSchema(items=post_schemas)

    except PostNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts found matching the criteria",
        )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@post_router.get("/posts/my")
async def get_my_posts(
    session: AsyncSessionDep, user: User = Depends(current_active_user)
) -> PostListResponseSchema:
    try:
        posts = await PostQueryBuilder.get_posts_by_user(session, user.id)
        return PostListResponseSchema(
            firstName=user.first_name, secondName=user.second_name, items=posts
        )
    except EmptyQueryResult:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    except UnauthorizedAccess:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@post_router.get("/posts/{post_id}", response_model=PostResponseSchema)
async def get_post_by_id(post_id: int, session: AsyncSessionDep):
    try:
        post = await PostQueryBuilder().get_post_by_id(session, post_id)
        return post
    except EmptyQueryResult:
        raise HTTPException(status_code=status.HTTP_204_NOT_FOUND)


@post_router.post(
    "/posts", status_code=status.HTTP_201_CREATED, response_model=PostResponseSchema
)
async def create_post(
    session: AsyncSessionDep,
    post_data: PostCreateSchema,
    current_user: User = Depends(current_active_user),
):
    new_post = await PostQueryBuilder.create_post(
        session, post_data=post_data, user_id=current_user.id
    )
    return PostResponseSchema.model_validate(new_post)


@post_router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    session: AsyncSessionDep, post_id: int, user: User = Depends(current_active_user)
):
    try:
        await PostQueryBuilder.delete_post(session, post_id, user.id)

    except PostNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    except UnauthorizedAccess:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
            )


@post_router.patch("/posts/{post_id}")
async def update_post(
    session: AsyncSessionDep,
    post_id: int,
    data: PostUpdateSchema,
    user: User = Depends(current_active_user),
):
    try:
        return await PostQueryBuilder.update_post(session, post_id, data, user.id)
    except PostNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    except UnauthorizedAccess:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)