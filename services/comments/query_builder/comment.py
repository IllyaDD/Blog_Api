
from sqlmodel import select

from common.errors import EmptyQueryResult
from services.comments.errors import CommentNotFound
from dependecies.session import AsyncSessionDep
from models import Comment

from services.comments. schemas import CommentResponseSchema, CommentCreateSchema, CommentListResponseSchema





class CommentQueryBuilder:
    
    @staticmethod
    async def create_com(session: AsyncSessionDep, com_data: CommentCreateSchema, user_id: int):
        com_dict = com_data.model_dump()
        com_dict['author_id'] = user_id
        
        if com_dict.get('parent_id') == 0:
            com_dict['parent_id'] = None
        
        com = Comment(**com_dict)
        session.add(com)
        await session.commit()
        await session.refresh(com)
        return com
    
    
    @staticmethod
    async def get_com_by_id(session:AsyncSessionDep, com_id:int):
        query = select(Comment).where(Comment.id == com_id)
        result =  await session.execute(query)
        com = result.scalar_one_or_none()
        if not com:
            raise EmptyQueryResult
        return com
    
    
    @staticmethod
    async def delete_com(session:AsyncSessionDep, com_id:int):
        com = await CommentQueryBuilder.get_com_by_id(session, com_id)
        await session.delete(com)
        await session.commit()