from sqlalchemy.orm import Session

from app.auth.schemas import UserLogin, UserRegister
from app.core.security import create_access_token, hash_password, verify_password
from app.users.models import User
from app.users.repository import create_user, get_user_by_email


def register_user(db: Session, user_data: UserRegister) -> User | None:
    # Registration owns the rule: one email can only create one account.
    existing_user = get_user_by_email(db, str(user_data.email))

    if existing_user is not None:
        return None

    return create_user(
        db,
        name=user_data.name,
        email=str(user_data.email),
        hashed_password=hash_password(user_data.password),
    )


def login_user(db: Session, login_data: UserLogin) -> str | None:
    # Login succeeds only when the email exists and the password matches the hash.
    user = get_user_by_email(db, str(login_data.email))

    if user is None:
        return None

    if not verify_password(login_data.password, user.hashed_password):
        return None

    return create_access_token(user.id)
