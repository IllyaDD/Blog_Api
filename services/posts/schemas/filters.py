from sqlmodel import SQLModel, Field


class PostFilter(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    author_id: int | None = Field(default=None)
    is_published: bool | None = Field(default=None)
