from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.session import get_db
from models.user import User
from schemas.dashboard_schema import DashboardKpiResponse, MetricValueResponse
from services.dashboard_service import get_dashboard_kpis_service


router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/kpis", response_model=DashboardKpiResponse)
def get_dashboard_kpis(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> DashboardKpiResponse:
	return get_dashboard_kpis_service(db)


@router.get("/total-executions", response_model=MetricValueResponse)
def get_total_executions(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> MetricValueResponse:
	data = get_dashboard_kpis_service(db)
	return MetricValueResponse(metric="total_executions", value=float(data.total_executions))


@router.get("/success-rate", response_model=MetricValueResponse)
def get_success_rate(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> MetricValueResponse:
	data = get_dashboard_kpis_service(db)
	return MetricValueResponse(metric="success_rate", value=data.success_rate)


@router.get("/failure-rate", response_model=MetricValueResponse)
def get_failure_rate(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> MetricValueResponse:
	data = get_dashboard_kpis_service(db)
	return MetricValueResponse(metric="failure_rate", value=data.failure_rate)


@router.get("/total-cost", response_model=MetricValueResponse)
def get_total_cost(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> MetricValueResponse:
	data = get_dashboard_kpis_service(db)
	return MetricValueResponse(metric="total_cost", value=data.total_cost)


@router.get("/total-tokens", response_model=MetricValueResponse)
def get_total_tokens(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> MetricValueResponse:
	data = get_dashboard_kpis_service(db)
	return MetricValueResponse(metric="total_tokens", value=float(data.total_tokens))


@router.get("/average-latency", response_model=MetricValueResponse)
def get_average_latency(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> MetricValueResponse:
	data = get_dashboard_kpis_service(db)
	return MetricValueResponse(metric="average_latency", value=data.average_latency)
