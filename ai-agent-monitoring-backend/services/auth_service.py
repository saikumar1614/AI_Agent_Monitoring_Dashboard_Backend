from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.config import settings
from core.security import create_access_token, get_password_hash, verify_password
from models.user import User
from schemas.auth_schema import LoginRequest, SignupRequest


def get_user_by_email(db: Session, email: str) -> User | None:
	return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
	return db.query(User).filter(User.username == username).first()


def signup_user(db: Session, payload: SignupRequest) -> User:
	if get_user_by_email(db, payload.email):
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="Email already registered",
		)

	if get_user_by_username(db, payload.username):
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="Username already taken",
		)

	user = User(
		username=payload.username,
		email=payload.email,
		hashed_password=get_password_hash(payload.password),
	)
	db.add(user)
	db.commit()
	db.refresh(user)
	return user


def login_user(db: Session, payload: LoginRequest) -> tuple[str, User]:
	user = get_user_by_email(db, payload.email)
	if user is None or not verify_password(payload.password, user.hashed_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid email or password",
		)

	token = create_access_token({"sub": str(user.id), "email": user.email})
	return token, user


def token_expiry_seconds() -> int:
	return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
