from sqlmodel import SQLModel
from typing import List

from services.comments.schemas import CommentResponseSchema
from datetime import datetime


class CommentLikesResponseSchema(CommentResponseSchema):
    liked_at: datetime


class CommentLikesListResponseSchema(SQLModel):
    items: List[CommentLikesResponseSchema]
