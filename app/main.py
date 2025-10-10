# app/main.py

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_307_TEMPORARY_REDIRECT

from . import crud, schemas
from .database import engine, AsyncSessionLocal
from .models import Base

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.post("/links", response_model=schemas.URLInfo)
async def create_short_url(
    url: schemas.URLCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):

    db_url = await crud.create_db_url(db, target_url=str(url.target_url))

    base_url = str(request.base_url)
    full_short_url = f"{base_url}links/{db_url.short_code}"

    response_object = {
        "id": db_url.id,
        "target_url": db_url.target_url,
        "created_at": db_url.created_at,
        "short_url": full_short_url,
        "clicks": db_url.clicks,
    }
    return response_object


@app.get("/links/{short_code}")
async def redirect_to_original(
    short_code: str, db: AsyncSession = Depends(get_db)
):

    db_url = await crud.get_url_by_short_code(db, short_code)

    if not db_url:
        raise HTTPException(status_code=404, detail="Link not found!")

    await crud.increment_clicks(db, db_url)

    return RedirectResponse(
        url=db_url.target_url, status_code=HTTP_307_TEMPORARY_REDIRECT
    )

@app.get("/links-clicks/{short_code}")
async def get_num_clicks(
    short_code: str, db: AsyncSession = Depends(get_db)
):

    db_url = await crud.get_url_by_short_code(db, short_code)

    if not db_url:
        raise HTTPException(status_code=404, detail="Link not found!")

    await crud.increment_clicks(db, db_url)

    return {"short_code": db_url.short_code, "clicks": db_url.clicks}