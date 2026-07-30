from fastapi import HTTPException, status


def conflict_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=message,
    )


def invalid_credentials_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def not_found_error(resource_name: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource_name} not found",
    )


def bad_request_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message,
    )
