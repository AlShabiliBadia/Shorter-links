from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import models

from .. import crud, schemas, password_utils, jwt_utils
from ..dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/signup", response_model=schemas.UserDisplay, status_code=status.HTTP_201_CREATED)
async def signup(user: schemas.UserAccount, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    new_user = await crud.create_db_user(db, user=user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login", response_model=schemas.Token)
async def login(login_info: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, email=login_info.email)

    if not db_user or not password_utils.verify_password(login_info.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = jwt_utils.create_access_token(
        data={"sub": str(db_user.id)}
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.delete("/account/delete", status_code=status.HTTP_200_OK)
async def delete_account(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await crud.delete_db_user(db=db, user=current_user)
    return {"detail": "Account deleted successfully"}