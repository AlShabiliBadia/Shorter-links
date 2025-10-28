from typing import Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from . import models, utils, schemas, password_utils

async def get_url_by_short_code(db: AsyncSession, short_code: str):
    result = await db.execute(
        select(models.URL).filter(models.URL.short_code == short_code)
    )
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(models.User).filter(models.User.email == email)
    )
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.User).filter(models.User.id == user_id)
    )
    return result.scalars().first()

async def get_url_by_short_code_and_lock(db: AsyncSession, short_code: str):
    result = await db.execute(
        select(models.URL)
        .filter(models.URL.short_code == short_code)
        .with_for_update()
    )
    return result.scalars().first()


async def increment_clicks(db: AsyncSession, db_url: models.URL):
    db_url.clicks += 1


async def create_db_url(db: AsyncSession, target_url: str, owner_id: Optional[int] = None) -> models.URL:
    for _ in range(5):
        short_code = utils.generate_short_code()
        db_url = models.URL(
            target_url=target_url, 
            short_code=short_code,
            owned_by=owner_id
        )
        db.add(db_url)
        try:
            await db.commit()
            await db.refresh(db_url)
            return db_url
        except IntegrityError:
            await db.rollback()
    raise HTTPException(status_code=500, detail="Could not generate a unique short code.")


async def create_db_user(db: AsyncSession, user: schemas.UserAccount) -> models.User:
    hashed_password = password_utils.hash_password(user.password)
    
    db_user = models.User(
        username=user.username, 
        email=user.email, 
        password=hashed_password
    )
    db.add(db_user)

    return db_user

async def delete_db_user(db: AsyncSession, user: models.User):
    await db.delete(user)
    await db.commit()