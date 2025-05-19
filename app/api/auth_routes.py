from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import models
from app.core import utils, auth
from app.db.database import get_db
from app.db import schemas

router = APIRouter()

# ─────────────────────────────────────────────────────────────────────────────
# Login Endpoint – Issues JWT Access Token
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates the user and returns a signed JWT access token.

    Parameters:
        form_data (OAuth2PasswordRequestForm): Contains username and password
        db (AsyncSession): Async SQLAlchemy session

    Returns:
        dict: Access token and token type for Authorization header
    """
    # Look up the user by username
    result = await db.execute(select(models.User).where(models.User.username == form_data.username))
    user = result.scalar_one_or_none()

    # Validate password
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Generate JWT token with subject as username
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ─────────────────────────────────────────────────────────────────────────────
# Register Endpoint – Creates a New User
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/users/", response_model=schemas.UserInDB)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user by storing their hashed password.

    Parameters:
        user (UserCreate): Contains username and raw password
        db (AsyncSession): Async SQLAlchemy session

    Returns:
        UserInDB: The created user object (excluding password)
    """
    # Hash the user's password
    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)

    # Add and persist the new user
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user
