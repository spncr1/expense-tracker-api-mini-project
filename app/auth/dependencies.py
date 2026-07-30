from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import invalid_credentials_error
from app.core.security import get_user_id_from_token
from app.database.session import get_db
from app.users.models import User
from app.users.repository import get_user_by_id


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    # Protected routes use this dependency to turn a Bearer token into a real User.
    if credentials is None:
        raise invalid_credentials_error()

    user_id = get_user_id_from_token(credentials.credentials)

    if user_id is None:
        raise invalid_credentials_error()

    user = get_user_by_id(db, user_id)

    if user is None:
        raise invalid_credentials_error()

    return user
