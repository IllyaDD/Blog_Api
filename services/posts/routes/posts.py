
from fastapi import APIRouter, Depends, status, HTTPException
from typing import List

from dependecies import session
from dependecies.session import AsyncSessionDep
from models import Post, post
from models.user import User
from services.posts.schemas import PostCreateSchema,PostListResponseSchema,PostResponseSchema, PostUpdateSchema
from common.schemas import PaginationParams
from services.posts.schemas.filters import PostFilter
from services.posts.query_builder import PostQueryBuilder
from common import EmptyQueryResult
from services.users.modules.manager import current_active_user

from services.posts.errors import PostNotFound



post_router = APIRouter()







