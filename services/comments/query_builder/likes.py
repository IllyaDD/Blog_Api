from typing import List
from sqlmodel import select
from common.errors import EmptyQueryResult
from models import CommentLike, Comment


from services.comments.errors import CommentNotFound
from dependecies.session import AsyncSessionDep


class CommentLikeQueryBuilder:

    @staticmethod
    async def create_like_for_comment(
        session: AsyncSessionDep, user_id: int, com_id: int
    ):
        existing_like = await CommentLikeQueryBuilder.get_com_like(
            session, user_id, com_id
        )

        if existing_like:
            return existing_like

        com_query = select(Comment).where(Comment.id == com_id)
        com_result = await session.execute(com_query)
        com = com_result.scalar_one_or_none()

        if not com:
            raise CommentNotFound

        like = CommentLike(user_id=user_id, comment_id=com_id)
        session.add(like)

        com.number_of_likes += 1

        await session.commit()
        await session.refresh(like)
        await session.refresh(com)
        return like

    @staticmethod
    async def get_com_like(session: AsyncSessionDep, user_id: int, com_id: int):
        query = select(CommentLike).where(
            CommentLike.comment_id == com_id, CommentLike.user_id == user_id
        )
        result = await session.execute(query)
        like = result.scalar_one_or_none()
        return like

    @staticmethod
    async def delete_like_from_com(session: AsyncSessionDep, com_id: int, user_id: int):
        like = await CommentLikeQueryBuilder.get_post_like(session, user_id, com_id)
        if not like:
            raise EmptyQueryResult("Like not found")

        com_query = select(Comment).where(Comment.id == com_id)
        result = await session.execute(com_query)
        com = result.scalar_one_or_none()

        if not com:
            raise EmptyQueryResult("Post not found")

        await session.delete(like)

        if com.number_of_likes > 0:
            com.number_of_likes -= 1

        await session.commit()
        await session.refresh(com)

    @staticmethod
    async def get_user_post_likes(session: AsyncSessionDep, user_id: int):

        query = (
            select(CommentLike)
            .where(CommentLike.user_id == user_id)
            .options(
                selectinload(CommentLike.comment).selectinload(Comment.author),
                selectinload(CommentLike.post).selectinload(Comment.likes),
            )
        )
        result = await session.execute(query)
        likes = result.scalars().all()
        if not likes:
            raise EmptyQueryResult
        return likes
