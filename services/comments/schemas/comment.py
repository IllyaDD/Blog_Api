from datetime import datetime
from logging import lastResort
from typing import List, Optional

from sqlmodel import SQLModel, Field


class CommentResponseSchema(SQLModel):
    id: int
    content: str
    author_id: int
    created_at: datetime
    post_id: int
    parent_id: Optional[int]


class CommentListResponseSchema(SQLModel):
    items: List[CommentResponseSchema]
    
    
class CommentCreateSchema(SQLModel):
    content: str
    author_id: int
    post_id: int
    parent_id: Optional[int]
    
    
