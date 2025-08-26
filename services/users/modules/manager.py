from typing import Optional

from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (
    BearerTransport,
    JWTStrategy,
    AuthenticationBackend,
)
from fastapi import Request, Depends

from common.settings import Settings
from dependecies.auth import get_user_db
from models import User


class UserManager(BaseUserManager[User, int]):
    reset_password_token_secret = (
        Settings().auth.reset_password_token_secret.get_secret_value()
    )
    verification_token_secret = (
        Settings().auth.verification_token_secret.get_secret_value()
    )

    async def on_after_register(self, user, request: Optional[Request] = None):
        print(f"User {user.email} has registered")

    async def on_after_forgot_password(
        self, user, token, request: Optional[Request] = None
    ):
        print(f"User: {user.email} forgot password. Reset token: {token}")

    async def on_after_request_verify(
        self, user, token, request: Optional[Request] = None
    ):
        print(f"User: {user.email} sended verification request. token: {token}")

    def parse_id(self, user_id):
        return int(user_id)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="users/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=Settings().auth.jwt_strategy_token_secret.get_secret_value(),
        lifetime_seconds=3600,
    )


auth_backend = AuthenticationBackend(
    name="jwt", transport=bearer_transport, get_strategy=get_jwt_strategy
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
current_active_user = fastapi_users.current_user(active=True)
