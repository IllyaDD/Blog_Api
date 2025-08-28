from sqlmodel import SQLModel
from typing import List


class CommentLikesResponseSchema(SQLModel):
    post_id: int


class CommentLikesListResponseSchema(SQLModel):
    items: List[CommentLikesResponseSchema]
