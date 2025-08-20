from contextlib import asynccontextmanager

from fastapi import FastAPI

from common.settings import Settings
from db.database import Database
from services.users.routes.user import users_router
from services.posts.routes.posts import post_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    database = Database(settings=Settings())
    yield
    await database.dispose(close=False)


app = FastAPI(lifespan=lifespan)


app.include_router(users_router)    
app.include_router(post_router, tags=['posts'])