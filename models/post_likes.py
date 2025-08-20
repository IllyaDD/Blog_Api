from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from sqlalchemy import VARCHAR, Column, DateTime
from datetime import datetime, timezone




class PostLike(SQLModel, table=True):
    __tablename__ = "post_likes"

    user_id: int = Field(primary_key=True, foreign_key="users.id")
    post_id: int = Field(primary_key=True, foreign_key="posts.id")
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    )

    user: "User" = Relationship(back_populates="post_likes")
    post: "Post" = Relationship(back_populates="likes")
    