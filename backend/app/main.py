from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from models import db_helper
from api import router as router_api


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await db_helper.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router_api)


if __name__ == "__main__":
    uvicorn.run("main:app")
