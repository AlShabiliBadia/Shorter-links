from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models, utils

async def get_url_by_short_code(db: AsyncSession, short_code: str):
    result = await db.execute(
        select(models.URL).filter(models.URL.short_code == short_code)
    )
    return result.scalars().first()

async def increment_clicks(db: AsyncSession, db_url: models.URL):
    db_url.clicks += 1
    await db.commit()
    await db.refresh(db_url)
    return db_url

async def create_db_url(db: AsyncSession, target_url: str) -> models.URL:
    while True:
        short_code = utils.generate_short_code()
        if not await get_url_by_short_code(db, short_code):
            break
    
    db_url = models.URL(target_url=target_url, short_code=short_code)
    db.add(db_url)
    await db.commit()
    await db.refresh(db_url)
    return db_url