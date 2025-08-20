from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from sqlalchemy import VARCHAR, Column, DateTime
from datetime import datetime, timezone






class CommentLike(SQLModel, table=True):
    __tablename__ = "comment_likes"

    user_id: int = Field(primary_key=True, foreign_key="users.id")
    comment_id: int = Field(primary_key=True, foreign_key="comments.id")
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    )

    user: "User" = Relationship(back_populates="comment_likes")
    comment: "Comment" = Relationship(back_populates="likes")