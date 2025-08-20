
from sqlmodel import DateTime, SQLModel, Field, Relationship
from typing import Optional, List
from sqlalchemy import VARCHAR, Column
from datetime import datetime, timezone


class Post(SQLModel, table=True):
    __tablename__ = "posts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column(VARCHAR(length=100), nullable=False))
    content: str = Field(sa_column=Column(VARCHAR(length=1000), nullable=False))
    author_id: Optional[int] = Field(default=None, foreign_key="users.id")
    number_of_likes: int = Field(default=0)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    )
    is_published: bool = Field(default=True)

    author: Optional['User'] = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")
    likes: List["PostLike"] = Relationship(back_populates="post")