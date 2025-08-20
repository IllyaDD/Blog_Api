from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel, Field





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
    is_published:bool
    number_of_likes:int


class PostListResponseSchema(SQLModel):
    items: List[PostResponseSchema]