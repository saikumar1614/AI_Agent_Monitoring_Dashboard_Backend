from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.session import get_db
from models.user import User
from schemas.auth_schema import (
	LoginRequest,
	SignupRequest,
	TokenResponse,
	TokenValidationResponse,
	UserResponse,
)
from services.auth_service import login_user, signup_user, token_expiry_seconds


router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> UserResponse:
	user = signup_user(db, payload)
	return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
	token, user = login_user(db, payload)
	return TokenResponse(
		access_token=token,
		token_type="bearer",
		expires_in=token_expiry_seconds(),
		user=UserResponse.model_validate(user),
	)


@router.get("/validate-token", response_model=TokenValidationResponse)
def validate_token(current_user: User = Depends(get_current_user)) -> TokenValidationResponse:
	return TokenValidationResponse(valid=True, user=UserResponse.model_validate(current_user))
