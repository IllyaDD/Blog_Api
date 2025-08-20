from typing import List
from sqlmodel import select
from sqlalchemy import Select

from common.errors import EmptyQueryResult
from dependecies.session import AsyncSessionDep
from models import Post
from services.posts.schemas import PostCreateSchema, PostUpdateSchema
from common.schemas import PaginationParams
from services.posts.schemas.filters import PostFilter


class PostQueryBuilder:
    @staticmethod
    async def get_posts_pagination(
        session: AsyncSessionDep, 
        pagination: PaginationParams, 
        filters: PostFilter
    ) -> List[Post]:
        query_offset = pagination.page * pagination.size
        query_limit = pagination.size
        
        select_query = PostQueryBuilder.apply_filters(select(Post), filters)
        select_query = select_query.offset(query_offset).limit(query_limit)
        
        result = await session.execute(select_query)
        posts = result.scalars().all()
        
        if not posts:
            raise EmptyQueryResult
        return posts
    
    @staticmethod
    def apply_filters(select_query: Select, filters: PostFilter) -> Select:
        if filters:
            if filters.title:
                select_query = select_query.where(Post.title.ilike(f'%{filters.title}%'))
            if filters.content:
                select_query = select_query.where(Post.content.ilike(f'%{filters.content}%'))
            if filters.author_id:
                select_query = select_query.where(Post.author_id == filters.author_id)
            if filters.is_published is not None:
                select_query = select_query.where(Post.is_published == filters.is_published)
        return select_query

    @staticmethod
    async def get_post_by_id(session: AsyncSessionDep, post_id: int) -> Post:
        query = select(Post).where(Post.id == post_id)
        result = await session.execute(query)
        post = result.scalar_one_or_none()
        if not post:
            raise EmptyQueryResult
        return post

    @staticmethod
    async def create_post(session:AsyncSessionDep, post_data:PostCreateSchema, user_id:int):
        post_dict = post_data.model_dump()
        post_dict['user_id'] = user_id
        post = Post(**post_data)
        session.add(post)
        await session.commit()
        await session.refresh()
        return post

    @staticmethod   
    async def update_post(
        session: AsyncSessionDep, 
        post_id: int, 
        post_data: PostUpdateSchema
    ) -> Post:
        post = await PostQueryBuilder.get_post_by_id(session, post_id)
        for key, value in post_data.model_dump(exclude_unset=True).items():
            setattr(post, key, value)
        await session.commit()
        await session.refresh(post)
        return post

    @staticmethod
    async def delete_post(session: AsyncSessionDep, post_id: int) -> None:
        post = await PostQueryBuilder.get_post_by_id(session, post_id)
        await session.delete(post)
        await session.commit()

    @staticmethod
    async def get_posts_by_author(
        session: AsyncSessionDep, 
        author_id: int, 
        pagination: PaginationParams
    ) -> List[Post]:
        query_offset = pagination.page * pagination.size
        query_limit = pagination.size
        
        query = select(Post).where(Post.author_id == author_id)
        query = query.offset(query_offset).limit(query_limit)
        
        result = await session.execute(query)
        posts = result.scalars().all()
        
        if not posts:
            raise EmptyQueryResult
        return posts