from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from core.config import settings
from database.session import get_db
from models.user import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
	return pwd_context.hash(password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
	to_encode = data.copy()
	expire = datetime.now(timezone.utc) + (
		expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	)
	to_encode.update({"exp": expire})
	return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
	try:
		return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
	except JWTError as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid or expired token",
			headers={"WWW-Authenticate": "Bearer"},
		) from exc


def get_current_user(
	token: str = Depends(oauth2_scheme),
	db: Session = Depends(get_db),
) -> User:
	payload = decode_access_token(token)
	user_id = payload.get("sub")

	if user_id is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid token payload",
			headers={"WWW-Authenticate": "Bearer"},
		)

	try:
		user_id_int = int(user_id)
	except (TypeError, ValueError) as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid token subject",
			headers={"WWW-Authenticate": "Bearer"},
		) from exc

	user = db.query(User).filter(User.id == user_id_int).first()
	if user is None or not user.is_active:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="User not found or inactive",
			headers={"WWW-Authenticate": "Bearer"},
		)

	return user
