from fastapi import APIRouter, Depends, status

from core.security import get_current_user
from models.user import User
from schemas.langfuse_schema import LangfuseCompletionTrackRequest, LangfuseTrackResponse
from services.langfuse_service import langfuse_tracker

router = APIRouter(prefix="/api/langfuse", tags=["Langfuse"])


@router.post("/track-completion", response_model=LangfuseTrackResponse, status_code=status.HTTP_200_OK)
def track_completion(
    payload: LangfuseCompletionTrackRequest,
    current_user: User = Depends(get_current_user),
) -> LangfuseTrackResponse:
    return langfuse_tracker.track_completion(payload, user_id=str(current_user.id))
