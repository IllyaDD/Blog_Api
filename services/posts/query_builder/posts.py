from typing import List, Optional
from sqlmodel import select
from sqlalchemy import Select, and_, or_

from common.errors import EmptyQueryResult
from dependecies.session import AsyncSessionDep
from models import Post
from services.posts.schemas import PostCreateSchema, PostUpdateSchema
from common.schemas import PaginationParams
from services.posts.schemas.filters import PostFilter
from sqlalchemy.orm import selectinload
from services.posts.errors import PostNotFound
from common.errors import UnauthorizedAccess
import httpx
from fastapi import HTTPException


class PostQueryBuilder:

    @staticmethod
    async def get_posts_pagination(
        session, pagination_params, filters: Optional[PostFilter] = None, current_user_id: int = None
    ) -> List[Post]:
        query_offset, query_limit = (
            pagination_params.page * pagination_params.size,
            pagination_params.size,
        )

        # Перевіряємо чи запит взагалі може повернути результати
        if filters and filters.is_published is False and current_user_id is None:
            # Неавторизований користувач намагається отримати неопубліковані пости
            raise EmptyQueryResult

        select_query = (
            PostQueryBuilder.apply_filters(select(Post), filters, current_user_id)
            .offset(query_offset)
            .limit(query_limit)
        )
        
        result = await session.execute(select_query)
        posts = result.scalars().all()
        
        if not posts:
            raise EmptyQueryResult
        return posts

    @staticmethod
    def apply_filters(select_query, filters: Optional[PostFilter] = None, current_user_id: int = None) -> Select:
        if not filters:
            # Якщо фільтрів немає, показуємо тільки опубліковані пости для неавторизованих
            if current_user_id is None:
                select_query = select_query.where(Post.is_published == True)
            return select_query

        # Застосовуємо текстові фільтри
        if filters.title:
            select_query = select_query.where(
                Post.title.ilike(f"%{filters.title}%")
            )
        if filters.content:
            select_query = select_query.where(
                Post.content.ilike(f"%{filters.content}%")
            )
        if filters.author_id:
            select_query = select_query.where(Post.author_id == filters.author_id)

        # Обробка фільтра is_published
        if filters.is_published is not None:
            if filters.is_published:
                # Шукаємо тільки опубліковані пости
                select_query = select_query.where(Post.is_published == True)
            else:
                # Шукаємо неопубліковані пости - тільки для авторизованих користувачів
                if current_user_id:
                    select_query = select_query.where(
                        Post.is_published == False,
                        Post.author_id == current_user_id
                    )
                else:
                    # Для неавторизованих - нічого не знайдемо
                    select_query = select_query.where(Post.id == -1)
        else:
            # Якщо is_published не вказано, визначаємо доступні пости
            if current_user_id is None:
                # Неавторизований користувач бачить тільки опубліковані пости
                select_query = select_query.where(Post.is_published == True)
            else:
                # Авторизований користувач бачить всі пости, але неопубліковані тільки свої
                select_query = select_query.where(
                    or_(
                        Post.is_published == True,
                        and_(
                            Post.is_published == False,
                            Post.author_id == current_user_id
                        )
                    )
                )

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
    async def get_post_by_content(
        session: AsyncSessionDep, post_content: str, current_user_id: int = None
    ) -> List[Post]:
        query = select(Post).where(Post.content.ilike(f"%{post_content}%"))

        if current_user_id:
            query = query.where(
                (Post.is_published == True)
                | ((Post.is_published == False) & (Post.author_id == current_user_id))
            )
        else:
            query = query.where(Post.is_published == True)

        result = await session.execute(query)
        posts = result.scalars().all()
        if not posts:
            raise EmptyQueryResult
        return posts

    @staticmethod
    async def get_post_by_name(
        session, post_name: str, current_user_id: int = None
    ) -> List[Post]:
        query = select(Post).where(Post.title.ilike(f"%{post_name}%"))

        if current_user_id:
            query = query.where(
                (Post.is_published == True)
                | ((Post.is_published == False) & (Post.author_id == current_user_id))
            )
        else:
            query = query.where(Post.is_published == True)

        result = await session.execute(query)
        posts = result.scalars().all()
        if not posts:
            raise EmptyQueryResult
        return posts

    @staticmethod
    async def create_post(
        session: AsyncSessionDep, post_data: PostCreateSchema, user_id: int
    ):
        post_dict = post_data.model_dump()
        post_dict["author_id"] = user_id

        post = Post(**post_dict)
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    @staticmethod
    async def update_post(
        session: AsyncSessionDep,
        post_id: int,
        post_data: PostUpdateSchema,
        user_id: int,
    ) -> Post:
        post = await PostQueryBuilder.get_post_by_id_check(session, post_id, user_id)
        for key, value in post_data.model_dump(exclude_unset=True).items():
            setattr(post, key, value)
        await session.commit()
        await session.refresh(post)
        return post

    @staticmethod
    async def delete_post(session: AsyncSessionDep, post_id: int, user_id: int) -> None:
        post = await PostQueryBuilder.get_post_by_id_check(session, post_id, user_id)
        await session.delete(post)
        await session.commit()

    @staticmethod
    async def get_posts_by_user(session: AsyncSessionDep, user_id: int) -> List[Post]:
        select_query = (
            select(Post)
            .where(Post.author_id == user_id)
            .options(
                selectinload(Post.author),
                selectinload(Post.comments),
                selectinload(Post.likes),
            )
        )
        query_result = await session.execute(select_query)
        posts = list(query_result.scalars())

        if not posts:
            raise EmptyQueryResult
        return posts

    @staticmethod
    async def get_user_noted_posts(
        session: AsyncSessionDep, user_id: int, pagination_params: PaginationParams
    ) -> List[Post]:
        query_offset, query_limit = (
            pagination_params.page * pagination_params.size,
            pagination_params.size,
        )

        select_query = (
            select(Post)
            .where(Post.author_id == user_id)
            .where(Post.is_published == False)
            .offset(query_offset)
            .limit(query_limit)
            .options(
                selectinload(Post.author),
                selectinload(Post.comments),
                selectinload(Post.likes),
            )
        )

        result = await session.execute(select_query)
        posts = result.scalars().all()

        if not posts:
            raise EmptyQueryResult

        return posts

    @staticmethod
    async def get_post_by_id_check(
        session: AsyncSessionDep, post_id: int, user_id: int
    ):
        query = select(Post).where(Post.id == post_id)
        result = await session.execute(query)
        post = result.scalar_one_or_none()
        if not post:
            raise PostNotFound
        if post.author_id != user_id:
            raise UnauthorizedAccess
        return post

    @staticmethod
    async def explain_post(session: AsyncSessionDep, post_id: int):
        post = await PostQueryBuilder.get_post_by_id(session, post_id)
        if not post:
            raise PostNotFound

        post_insides: str = (
            f"Title of the post {post.title}, content of the post {post.content}"
        )

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                "http://localhost:11434/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "mistral",
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Explain this post: {post_insides}",
                        }
                    ],
                    "stream": False,
                },
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Mistral API error: {response.text}",
                )