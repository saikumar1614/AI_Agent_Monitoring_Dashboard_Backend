from datetime import datetime

from sqlalchemy.orm import Session

from models.execution import Execution


def get_execution_by_id(db: Session, execution_id: int) -> Execution | None:
    return db.query(Execution).filter(Execution.id == execution_id).first()


def list_executions(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status: str | None = None,
    agent_id: int | None = None,
) -> tuple[list[Execution], int]:
    query = db.query(Execution)

    if status is not None:
        query = query.filter(Execution.status == status)

    if agent_id is not None:
        query = query.filter(Execution.agent_id == agent_id)

    total = query.count()
    items = query.order_by(Execution.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def create_execution(
    db: Session,
    agent_id: int,
    status: str,
    execution_metadata: dict | None = None,
    started_at: datetime | None = None,
    completed_at: datetime | None = None,
) -> Execution:
    execution = Execution(
        agent_id=agent_id,
        status=status,
        execution_metadata=execution_metadata,
        started_at=started_at,
        completed_at=completed_at,
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution


def update_execution(
    db: Session,
    execution_id: int,
    status: str | None = None,
    execution_metadata: dict | None = None,
    started_at: datetime | None = None,
    completed_at: datetime | None = None,
) -> Execution | None:
    execution = get_execution_by_id(db, execution_id)
    if not execution:
        return None

    if status is not None:
        execution.status = status
    if execution_metadata is not None:
        execution.execution_metadata = execution_metadata
    if started_at is not None:
        execution.started_at = started_at
    if completed_at is not None:
        execution.completed_at = completed_at

    db.commit()
    db.refresh(execution)
    return execution


def delete_execution(db: Session, execution_id: int) -> bool:
    execution = get_execution_by_id(db, execution_id)
    if not execution:
        return False

    db.delete(execution)
    db.commit()
    return True
