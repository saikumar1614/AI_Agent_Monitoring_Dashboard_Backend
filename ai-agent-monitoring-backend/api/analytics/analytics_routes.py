from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.session import get_db
from models.user import User
from schemas.analytics_schema import LatencyAggregationResponse
from services.analytics_service import get_daily_latency_service, get_hourly_latency_service


router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/latency/hourly", response_model=LatencyAggregationResponse)
def get_hourly_latency(
	start_date: date = Query(...),
	end_date: date = Query(...),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> LatencyAggregationResponse:
	return get_hourly_latency_service(db, start_date=start_date, end_date=end_date)


@router.get("/latency/daily", response_model=LatencyAggregationResponse)
def get_daily_latency(
	start_date: date = Query(...),
	end_date: date = Query(...),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> LatencyAggregationResponse:
	return get_daily_latency_service(db, start_date=start_date, end_date=end_date)
