import asyncio

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.session import SessionLocal, get_db
from models.user import User
from schemas.live_schema import LiveMetricsResponse
from services.dashboard_service import get_dashboard_kpis_service
from services.live_service import get_recent_execution_payload, get_ws_user_from_token, utc_now


router = APIRouter(prefix="/api/live", tags=["Live"])


@router.get("/metrics", response_model=LiveMetricsResponse, status_code=status.HTTP_200_OK)
def get_live_metrics(
    refresh_interval_seconds: int = Query(5, ge=1, le=300),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LiveMetricsResponse:
    kpis = get_dashboard_kpis_service(db)
    return LiveMetricsResponse(
        total_executions=kpis.total_executions,
        success_rate=kpis.success_rate,
        failure_rate=kpis.failure_rate,
        total_cost=kpis.total_cost,
        total_tokens=kpis.total_tokens,
        average_latency=kpis.average_latency,
        generated_at=utc_now(),
        refresh_interval_seconds=refresh_interval_seconds,
    )


@router.websocket("/ws/executions")
async def stream_live_executions(websocket: WebSocket) -> None:
    await websocket.accept()

    refresh_raw = websocket.query_params.get("refresh_interval_seconds", "5")
    limit_raw = websocket.query_params.get("limit", "20")
    token = websocket.query_params.get("token", "")

    try:
        refresh_interval_seconds = max(1, min(300, int(refresh_raw)))
        limit = max(1, min(100, int(limit_raw)))
    except ValueError:
        await websocket.close(code=1003, reason="Invalid query parameters")
        return

    db = SessionLocal()
    try:
        try:
            user = get_ws_user_from_token(db, token)
        except Exception:
            await websocket.close(code=1008, reason="Unauthorized")
            return

        while True:
            executions = get_recent_execution_payload(db, limit=limit)
            kpis = get_dashboard_kpis_service(db)

            await websocket.send_json(
                {
                    "type": "live_execution_stream",
                    "user_id": user.id,
                    "generated_at": utc_now().isoformat(),
                    "refresh_interval_seconds": refresh_interval_seconds,
                    "executions": executions,
                    "metrics": kpis.model_dump(mode="json"),
                }
            )

            await asyncio.sleep(refresh_interval_seconds)
    except WebSocketDisconnect:
        pass
    finally:
        db.close()