from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.incident import Incident
from backend.models.incident_event import IncidentEvent
from sqlalchemy import select

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

def get_by_external_identity(
    db: Session,
    *,
    source: str,
    external_id: str,
) -> Incident | None:
    statement = (
        select(Incident)
        .where(
            Incident.source == source,
            Incident.external_id == external_id,
        )
    )

    return db.scalar(statement)


def get_event_by_external_identity(
    db: Session,
    *,
    incident_id: int,
    source: str,
    external_id: str,
) -> IncidentEvent | None:
    statement = (
        select(IncidentEvent)
        .where(
            IncidentEvent.incident_id == incident_id,
            IncidentEvent.source == source,
            IncidentEvent.external_id == external_id,
        )
    )

    return db.scalar(statement)


def create_import_incident(
    db: Session,
    *,
    data: dict,
) -> Incident:
    incident = Incident(**data)

    db.add(incident)

    # Sends INSERT to PostgreSQL,
    # but does NOT commit the transaction.
    db.flush()

    return incident


def update_import_incident(
    db: Session,
    *,
    incident: Incident,
    updates: dict,
) -> Incident:
    for field, value in updates.items():
        setattr(incident, field, value)

    db.flush()

    return incident


def create_import_event(
    db: Session,
    *,
    incident_id: int,
    data: dict,
) -> IncidentEvent:
    event = IncidentEvent(
        incident_id=incident_id,
        **data,
    )

    db.add(event)
    db.flush()

    return event


def update_import_event(
    db: Session,
    *,
    event: IncidentEvent,
    updates: dict,
) -> IncidentEvent:
    for field, value in updates.items():
        setattr(event, field, value)

    db.flush()

    return event
    
def get_by_external_identity(
    db: Session,
    *,
    source: str,
    external_id: str,
) -> Incident | None:
    statement = (
        select(Incident)
        .where(
            Incident.source == source,
            Incident.external_id == external_id,
        )
    )

    return db.scalar(statement)


def get_event_by_external_identity(
    db: Session,
    *,
    incident_id: int,
    source: str,
    external_id: str,
) -> IncidentEvent | None:
    statement = (
        select(IncidentEvent)
        .where(
            IncidentEvent.incident_id == incident_id,
            IncidentEvent.source == source,
            IncidentEvent.external_id == external_id,
        )
    )

    return db.scalar(statement)

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