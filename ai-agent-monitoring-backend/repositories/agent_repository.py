from sqlalchemy.orm import Session

from models.agent import Agent


def get_agent_by_id(db: Session, agent_id: int) -> Agent | None:
    return db.query(Agent).filter(Agent.id == agent_id).first()


def get_agent_by_name(db: Session, name: str) -> Agent | None:
    return db.query(Agent).filter(Agent.name == name).first()


def list_agents(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    is_active: bool | None = None,
) -> tuple[list[Agent], int]:
    query = db.query(Agent)
    if is_active is not None:
        query = query.filter(Agent.is_active == is_active)
    
    total = query.count()
    agents = query.offset(skip).limit(limit).order_by(Agent.created_at.desc()).all()
    return agents, total


def create_agent(db: Session, name: str, version: str, description: str | None = None, owner_team: str | None = None) -> Agent:
    agent = Agent(
        name=name,
        version=version,
        description=description,
        owner_team=owner_team,
        is_active=True,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def update_agent(
    db: Session,
    agent_id: int,
    name: str | None = None,
    version: str | None = None,
    description: str | None = None,
    owner_team: str | None = None,
    is_active: bool | None = None,
) -> Agent | None:
    agent = get_agent_by_id(db, agent_id)
    if not agent:
        return None
    
    if name is not None:
        agent.name = name
    if version is not None:
        agent.version = version
    if description is not None:
        agent.description = description
    if owner_team is not None:
        agent.owner_team = owner_team
    if is_active is not None:
        agent.is_active = is_active
    
    db.commit()
    db.refresh(agent)
    return agent


def delete_agent(db: Session, agent_id: int) -> bool:
    agent = get_agent_by_id(db, agent_id)
    if not agent:
        return False
    
    db.delete(agent)
    db.commit()
    return True
