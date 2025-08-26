from sqlmodel import SQLModel, Field


class PaginationParams(SQLModel):
    page: int = Field(default=0, ge=0)
    size: int = Field(default=100, gt=1, lt=100000)
