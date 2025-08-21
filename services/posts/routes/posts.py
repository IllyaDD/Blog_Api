
from fastapi import APIRouter, Depends, status, HTTPException
from typing import List

from dependecies import session
from dependecies.session import AsyncSessionDep
from models import Post, post
from models.user import User
from services.posts.schemas import PostCreateSchema,PostListResponseSchema,PostResponseSchema, PostUpdateSchema
from common.schemas import PaginationParams
from services.posts.schemas.filters import PostFilter
from services.posts.query_builder import PostQueryBuilder
from common import EmptyQueryResult
from services.users.modules.manager import current_active_user

from services.posts.errors import PostNotFound



post_router = APIRouter()

@post_router.get("/my/posts")  
async def get_my_posts(
        session: AsyncSessionDep,
        user: User = Depends(current_active_user)
) -> PostListResponseSchema:
        try:
                posts = await PostQueryBuilder.get_posts_by_user(session, user.id)
                return PostListResponseSchema(
                firstName=user.first_name, 
                secondName=user.second_name, 
                items=posts
                )
        except EmptyQueryResult:
                raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
        
@post_router.get('/users/{user_id}/posts')
async def get_user_posts(session:AsyncSessionDep, user_id:int, user:User = Depends(current_active_user)) -> PostListResponseSchema:
        try:
                posts = await PostQueryBuilder.get_posts_by_user(session, user_id)
                return PostListResponseSchema(firstName=user.first_name, secondName=user.second_name, items=posts)
        except EmptyQueryResult:
                raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

        
        

@post_router.get('/posts/{post_id}', response_model=PostResponseSchema)
async def get_post(
        post_id: int,
        session: AsyncSessionDep
):
        try:
                post = await PostQueryBuilder().get_post_by_id(session, post_id)
                return post
        except EmptyQueryResult:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@post_router.post('/posts', status_code=status.HTTP_201_CREATED, response_model=PostResponseSchema)
async def create_post(
session: AsyncSessionDep, 
post_data: PostCreateSchema, 
current_user: User = Depends(current_active_user)
):
        post = Post(**post_data.dict(), author_id=current_user.id)
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post



@post_router.delete('/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(session:AsyncSessionDep,
                post_id:int, 
                user:User = Depends(current_active_user)
):
        try:
                await PostQueryBuilder.delete_post(session, post_id)
                
        except PostNotFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Shelf not found')
        
@post_router.patch('/posts/{post_id}')
async def update_post(session:AsyncSessionDep, post_id:int, data:PostUpdateSchema, user:User = Depends(current_active_user)):
        try:
                return await PostQueryBuilder.update_post(session, post_id, data)
        except PostNotFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")