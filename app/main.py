from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_307_TEMPORARY_REDIRECT
from fastapi.security import OAuth2PasswordBearer

from typing import Optional

from . import crud, schemas, password_utils, jwt_utils, models
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> Optional[models.User]:
    if token is None:
        return None

    try:
        payload = jwt_utils.jwt.decode(
            token, jwt_utils.SECRET_KEY, algorithms=[jwt_utils.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except jwt_utils.JWTError:
        return None

    user = await crud.get_user_by_id(db, user_id=int(user_id))
    return user


@app.post("/signup", response_model=schemas.UserDisplay, status_code=status.HTTP_201_CREATED)
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

@app.post("/login")
async def login(login_info: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, email=login_info.email)

    if not db_user or not password_utils.verify_password(login_info.password, db_user.password):
        raise HTTPException(
            status_code=401, 
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = jwt_utils.create_access_token(
        data={"sub": str(db_user.id)}
    )

    return {"access_token": access_token, "token_type": "bearer"}



@app.post("/links", response_model=schemas.URLInfo)
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
    return response_object


@app.get("/links/{short_code}")
async def redirect_to_original(
    short_code: str, db: AsyncSession = Depends(get_db)
):

    db_url = await crud.get_url_by_short_code(db, short_code)

    if not db_url:
        raise HTTPException(status_code=404, detail="Link not found!")

    await crud.increment_clicks(db, db_url)
    await db.commit()

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

    return {"target":db_url.target_url, "short_code": db_url.short_code, "clicks": db_url.clicks}