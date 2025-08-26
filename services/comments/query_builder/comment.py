from sqlmodel import select

from common.errors import EmptyQueryResult
from services.comments.errors import CommentNotFound
from dependecies.session import AsyncSessionDep
from models import Comment

from services.comments.schemas import (
    CommentResponseSchema,
    CommentCreateSchema,
    CommentListResponseSchema,
    CommentUpdateSchema,
)
from common import UnauthorizedAccess


class CommentQueryBuilder:

    @staticmethod
    async def create_com(
        session: AsyncSessionDep, com_data: CommentCreateSchema, user_id: int
    ):
        com_dict = com_data.model_dump()
        com_dict["author_id"] = user_id

        if com_dict.get("parent_id") == 0:
            com_dict["parent_id"] = None

        com = Comment(**com_dict)
        session.add(com)
        await session.commit()
        await session.refresh(com)
        return com

    @staticmethod
    async def get_com_by_id(session: AsyncSessionDep, com_id: int):
        query = select(Comment).where(Comment.id == com_id)
        result = await session.execute(query)
        com = result.scalar_one_or_none()
        if not com:
            raise EmptyQueryResult
        return com

    @staticmethod
    async def get_com_by_id_with_author_check(
        session: AsyncSessionDep, com_id: int, user_id: int
    ):
        query = select(Comment).where(Comment.id == com_id)
        result = await session.execute(query)
        com = result.scalar_one_or_none()

        if not com:
            raise CommentNotFound

        if com.author_id != user_id:
            raise UnauthorizedAccess

        return com

    @staticmethod
    async def delete_com(session: AsyncSessionDep, com_id: int, user_id: int):
        com = await CommentQueryBuilder.get_com_by_id_with_author_check(
            session, com_id, user_id
        )
        await session.delete(com)
        await session.commit()

    @staticmethod
    async def update_com(
        session: AsyncSessionDep,
        com_data: CommentUpdateSchema,
        com_id: int,
        user_id: int,
    ) -> Comment:
        com = await CommentQueryBuilder.get_com_by_id_with_author_check(
            session, com_id, user_id
        )
        for key, value in com_data.model_dump(exclude_unset=True).items():
            setattr(com, key, value)
        await session.commit()
        await session.refresh(com)
        return com
