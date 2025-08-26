from fastapi import APIRouter

from services.users.modules.manager import fastapi_users, auth_backend
from services.users.schemas import UserRead, UserCreate, UserUpdate

users_router = APIRouter()


users_router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/users/jwt", tags=["users"]
)
users_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/users",
    tags=["users"],
)
users_router.include_router(
    fastapi_users.get_reset_password_router(), prefix="/users", tags=["users"]
)
users_router.include_router(
    fastapi_users.get_verify_router(UserRead), prefix="/users", tags=["users"]
)
users_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
