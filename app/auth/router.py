from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import TokenRead, UserLogin, UserRead, UserRegister
from app.auth.service import login_user, register_user
from app.core.exceptions import conflict_error, invalid_credentials_error
from app.database.session import get_db
from app.users.models import User


router = APIRouter(prefix="/auth", tags=["auth"])

# Auth endpoints
@router.post( 
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserRegister,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    # Router turns service outcomes into HTTP responses.
    user = register_user(db, user_data)

    if user is None:
        raise conflict_error("Email already registered")

    return user


@router.post("/login", response_model=TokenRead)
async def login(
    login_data: UserLogin,
    db: Annotated[Session, Depends(get_db)],
) -> TokenRead:
    # The token returned here is what clients send to protected routes later.
    access_token = login_user(db, login_data)

    if access_token is None:
        raise invalid_credentials_error()

    return TokenRead(access_token=access_token)


@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
