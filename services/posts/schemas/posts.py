from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel, Field

from services.comments.schemas import CommentResponseSchema



class PostCreateSchema(SQLModel):
    title: str
    content: str
    is_published: bool

class PostUpdateSchema(SQLModel):
    title: Optional[str]
    content: Optional[str]
    is_published: Optional[bool]


class PostResponseSchema(SQLModel):
    id:int
    title:str
    content:str
    author_id:int
    created_at:datetime
    author_id:int
    is_published:bool
    number_of_likes:int


class PostListResponseSchema(SQLModel):
    firstName: Optional[str] = None
    secondName: Optional[str] = None
    items: List[PostResponseSchema]