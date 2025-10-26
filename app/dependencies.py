from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from jose import JWTError, jwt

from .database import AsyncSessionLocal
from . import crud, models, jwt_utils

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login", auto_error=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> Optional[models.User]:
    if token is None:
        return None

    try:
        payload = jwt.decode(
            token, jwt_utils.SECRET_KEY, algorithms=[jwt_utils.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None

    user = await crud.get_user_by_id(db, user_id=int(user_id))
    return user

async def get_current_active_user(
    current_user: Optional[models.User] = Depends(get_current_user),
) -> models.User:
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user