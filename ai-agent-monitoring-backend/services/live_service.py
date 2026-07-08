from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import decode_access_token
from models.execution import Execution
from models.user import User
from schemas.execution_schema import ExecutionResponse


def get_recent_execution_payload(db: Session, limit: int = 20) -> list[dict]:
    executions = db.query(Execution).order_by(Execution.created_at.desc()).limit(limit).all()
    return [ExecutionResponse.model_validate(item).model_dump(mode="json") for item in executions]


def get_ws_user_from_token(db: Session, token: str) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
        )

    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        ) from exc

    user = db.query(User).filter(User.id == user_id_int).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


def utc_now() -> datetime:
    return datetime.now(timezone.utc)