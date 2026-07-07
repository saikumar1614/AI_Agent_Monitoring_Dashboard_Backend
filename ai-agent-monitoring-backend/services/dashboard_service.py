from sqlalchemy.orm import Session

from repositories.analytics_repository import get_dashboard_kpis
from schemas.dashboard_schema import DashboardKpiResponse


def get_dashboard_kpis_service(db: Session) -> DashboardKpiResponse:
	values = get_dashboard_kpis(db)
	return DashboardKpiResponse(
		total_executions=int(values["total_executions"]),
		success_rate=round(float(values["success_rate"]), 2),
		failure_rate=round(float(values["failure_rate"]), 2),
		total_cost=round(float(values["total_cost"]), 6),
		total_tokens=int(values["total_tokens"]),
		average_latency=round(float(values["average_latency"]), 2),
	)
