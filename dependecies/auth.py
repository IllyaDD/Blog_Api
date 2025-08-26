from typing import AsyncGenerator

from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from dependecies.session import AsyncSessionDep
from models import User


async def get_user_db(
    session: AsyncSessionDep,
) -> AsyncGenerator[SQLAlchemyUserDatabase[int, User], None]:
    yield SQLAlchemyUserDatabase(session, User)
