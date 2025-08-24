from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from sqlalchemy import VARCHAR, Column, DateTime
from datetime import datetime, timezone

class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(sa_column=Column(VARCHAR(length=500), nullable=False))
    post_id: int = Field(default=None, foreign_key="posts.id")
    author_id: int = Field(default=None, foreign_key="users.id") 
    parent_id: Optional[int] = Field(default=None, foreign_key="comments.id")
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    )
    number_of_likes: int = Field(default=0)

    post: Optional['Post'] = Relationship(back_populates="comments")
    author: Optional['User'] = Relationship(back_populates="comments")
    likes: List["CommentLike"] = Relationship(back_populates="comment")
    
    parent: Optional['Comment'] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Comment.id"}
    )
    children: List['Comment'] = Relationship(back_populates="parent")