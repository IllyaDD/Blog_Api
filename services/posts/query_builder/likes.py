from typing import List
from sqlmodel import select
from common.errors import EmptyQueryResult
from models import PostLike, Post
from sqlalchemy.orm import selectinload
from services.posts.errors import PostNotFound
from dependecies.session import AsyncSessionDep


class PostLikesQueryBuilder:
    @staticmethod
    async def create_like_for_post(
        session: AsyncSessionDep, user_id: int, post_id: int
    ):

        existing_like = await PostLikesQueryBuilder.get_post_like(
            session, user_id, post_id
        )
        if existing_like:
            return existing_like

        post_query = select(Post).where(Post.id == post_id)
        post_result = await session.execute(post_query)
        post = post_result.scalar_one_or_none()

        if not post:
            raise PostNotFound

        like = PostLike(
            user_id=user_id,
            post_id=post_id,
        )
        session.add(like)

        post.number_of_likes += 1

        await session.commit()
        await session.refresh(like)
        await session.refresh(post)
        return like

    @staticmethod
    async def delete_like_from_post(
        session: AsyncSessionDep, post_id: int, user_id: int
    ):
        like = await PostLikesQueryBuilder.get_post_like(session, user_id, post_id)
        if not like:
            raise EmptyQueryResult("Like not found")

        post_query = select(Post).where(Post.id == post_id)
        post_result = await session.execute(post_query)
        post = post_result.scalar_one_or_none()

        if not post:
            raise EmptyQueryResult("Post not found")

        await session.delete(like)

        if post.number_of_likes > 0:
            post.number_of_likes -= 1

        await session.commit()
        await session.refresh(post)

    @staticmethod
    async def get_post_like(session: AsyncSessionDep, user_id: int, post_id: int):
        query = select(PostLike).where(
            PostLike.post_id == post_id, PostLike.user_id == user_id
        )
        result = await session.execute(query)
        like = result.scalar_one_or_none()
        return like

    @staticmethod
    async def get_user_post_likes(session: AsyncSessionDep, user_id: int):

        query = (
            select(PostLike)
            .where(PostLike.user_id == user_id)
            .options(
                selectinload(PostLike.post).selectinload(Post.author),
                selectinload(PostLike.post).selectinload(Post.comments),
                selectinload(PostLike.post).selectinload(Post.likes),
            )
        )
        result = await session.execute(query)
        likes = result.scalars().all()
        if not likes:
            raise EmptyQueryResult
        return likes
