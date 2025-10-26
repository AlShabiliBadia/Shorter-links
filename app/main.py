from fastapi import FastAPI
from .database import engine
from .models import Base
from .routers import links, users

app = FastAPI()

app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)
app.include_router(
    links.router,
    prefix="/links",
    tags=["Links"]
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "URL Shortener API is running."}