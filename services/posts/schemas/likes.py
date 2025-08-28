from sqlmodel import SQLModel
from typing import List
from datetime import datetime
from services.posts.schemas import PostResponseSchema


class LikedPostResponseSchema(PostResponseSchema):
    liked_at: datetime


class LikedPostsListResponseSchema(SQLModel):
    items: List[LikedPostResponseSchema]
