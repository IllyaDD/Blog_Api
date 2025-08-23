from typing import List
from sqlmodel import select
from sqlalchemy import Select

from common.errors import EmptyQueryResult
from dependecies.session import AsyncSessionDep
from models import Post
from services.posts.schemas import PostCreateSchema, PostUpdateSchema
from common.schemas import PaginationParams
from services.posts.schemas.filters import PostFilter
from sqlalchemy.orm import selectinload
from services.posts.errors import PostNotFound
class PostQueryBuilder:
    
    
    
    @staticmethod
    async def get_posts_pagination(session, pagination_params, filters) -> List[Post]:
        query_offset, query_limit = pagination_params.page * pagination_params.size, pagination_params.size
        select_query = PostQueryBuilder.apply_filters(select(Post), filters).offset(query_offset).limit(query_limit)
        result = await session.execute(select_query)
        posts = result.scalars().all()
        if not posts:
            raise EmptyQueryResult
        return posts
    
    @staticmethod
    def apply_filters(select_query, filters) -> Select:
        if filters and filters.title:
            select_query = select_query.where(Post.title.ilike(f'%{filters.title}%'))
        if filters and filters.author_id:
            select_query = select_query.where(Post.author_id == filters.author_id)
        if filters and filters.is_published is not None:
            select_query = select_query.where(Post.is_published == filters.is_published)
        return select_query
    


    @staticmethod
    async def get_post_by_id(session: AsyncSessionDep, post_id: int) -> Post:
        query = select(Post).where(Post.id == post_id)
        result = await session.execute(query)
        post = result.scalar_one_or_none()
        if not post:
            raise PostNotFound
        return post
    
    
    @staticmethod
    async def get_post_by_content(session: AsyncSessionDep, post_content: str) -> List[Post]:
        query = select(Post).where(Post.content.ilike(f'%{post_content}%')) 
        result = await session.execute(query)
        posts = result.scalars().all()
        if not posts:
            raise PostNotFound
        return posts
    
    
    
    
    @staticmethod
    async def get_post_by_name(session, post_name: str) -> Post:
        query = select(Post).where(Post.title.ilike(f'%{post_name}%'))
        result = await session.execute(query)
        post = result.scalars().all()
        if not post:
            raise PostNotFound
        return post

    
    

    @staticmethod
    async def create_post(session: AsyncSessionDep, post_data: PostCreateSchema, user_id: int):
            post_dict = post_data.model_dump()
            post_dict['author_id'] = user_id
            
            post = Post(**post_dict)
            session.add(post)
            await session.commit()
            await session.refresh(post)
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
    async def get_posts_by_user(
        session: AsyncSessionDep,
        user_id: int
) -> List[Post]:
        select_query = (
            select(Post)
            .where(Post.author_id == user_id)
            .options(
                selectinload(Post.author),
                selectinload(Post.comments),
                selectinload(Post.likes)
            )
        )
        query_result = await session.execute(select_query)
        posts = list(query_result.scalars())
        
        if not posts:
            raise EmptyQueryResult
        return posts
    
    
    
    
    
    
    @staticmethod
    async def get_user_noted_posts(
        session: AsyncSessionDep,
        user_id: int,
        pagination_params: PaginationParams
    ) -> List[Post]:
        """Get draft posts (is_published=False) for specific user"""
        query_offset, query_limit = pagination_params.page * pagination_params.size, pagination_params.size
        
        select_query = (
            select(Post)
            .where(Post.author_id == user_id)
            .where(Post.is_published == False)
            .offset(query_offset)
            .limit(query_limit)
            .options(
                selectinload(Post.author),
                selectinload(Post.comments),
                selectinload(Post.likes)
            )
        )
        
        result = await session.execute(select_query)
        posts = result.scalars().all()
        
        if not posts:
            raise EmptyQueryResult
        
        return posts