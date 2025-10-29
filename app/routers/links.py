from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_307_TEMPORARY_REDIRECT
from typing import Optional

from .. import crud, schemas, models
from ..dependencies import get_db, get_current_user, get_current_active_user

router = APIRouter()

@router.post("/", response_model=schemas.URLInfo)
async def create_short_url(
    url: schemas.URLCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user),
):
    owner_id = None
    if current_user:
        owner_id = current_user.id

    db_url = await crud.create_db_url(
        db, target_url=str(url.target_url), owner_id=owner_id
    )

    base_url = str(request.base_url)
    full_short_url = f"{base_url}links/{db_url.short_code}"

    return schemas.URLInfo(
        id=db_url.url_id,
        target_url=db_url.target_url,
        short_url=full_short_url,
        clicks=db_url.clicks,
        created_at=db_url.created_at
    )

@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str, db: AsyncSession = Depends(get_db)
):
    db_url = await crud.get_url_by_short_code_and_lock(db, short_code)

    if not db_url:
        raise HTTPException(status_code=404, detail="Link not found!")

    await crud.increment_clicks(db, db_url)
    await db.commit()

    return RedirectResponse(
        url=db_url.target_url, status_code=HTTP_307_TEMPORARY_REDIRECT
    )

@router.get("/clicks/{short_code}", response_model=schemas.URLStats)
async def get_num_clicks(
    short_code: str, 
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_url = await crud.get_url_by_short_code(db, short_code)

    if not db_url:
        raise HTTPException(status_code=404, detail="Link not found!")

    if db_url.owned_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view stats for this link."
        )

    return {
        "target_url": db_url.target_url,
        "short_code": db_url.short_code,
        "clicks": db_url.clicks,
    }
