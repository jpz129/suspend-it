"""Stub of Component A's auth surface: User with `.id` and get_current_user."""

from fastapi import HTTPException, status


class User:
    def __init__(self, id: int, email: str = "user@example.com") -> None:
        self.id = id
        self.email = email


def get_current_user() -> User:
    """Placeholder; tests replace this via FastAPI dependency_overrides."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
