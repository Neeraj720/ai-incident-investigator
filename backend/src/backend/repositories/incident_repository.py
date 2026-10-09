from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.incident import Incident
from backend.models.incident_event import IncidentEvent


def create_incident(db: Session, *, data: dict) -> Incident:
    incident = Incident(**data)
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def list_incidents(db: Session, *, project_ids: list[int]) -> list[Incident]:
    statement = (
        select(Incident)
        .where(Incident.project_id.in_(project_ids))
        .order_by(Incident.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_incident(db: Session, *, incident_id: int) -> Incident | None:
    return db.get(Incident, incident_id)


def update_incident(
    db: Session, *, incident: Incident, updates: dict
) -> Incident:
    for field, value in updates.items():
        setattr(incident, field, value)

    db.commit()
    db.refresh(incident)
    return incident


def delete_incident(db: Session, *, incident: Incident) -> None:
    db.delete(incident)
    db.commit()


def create_event(
    db: Session, *, incident_id: int, data: dict
) -> IncidentEvent:
    event = IncidentEvent(incident_id=incident_id, **data)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_events(
    db: Session, *, incident_id: int
) -> list[IncidentEvent]:
    statement = (
        select(IncidentEvent)
        .where(IncidentEvent.incident_id == incident_id)
        .order_by(IncidentEvent.occurred_at.asc())
    )
    return list(db.scalars(statement).all())