from sqlalchemy.orm import Session

from backend.models.user import User
from backend.schemas.incident import IncidentCreate, IncidentUpdate
from backend.services import incident_service


def create_incident(db: Session, user: User, data: IncidentCreate):
    return incident_service.create_incident(
        db, data=data, current_user=user
    )


def list_incidents(db: Session, user: User):
    return incident_service.list_incidents(db, current_user=user)


def get_incident(db: Session, user: User, incident_id: int):
    return incident_service.get_incident(
        db, incident_id=incident_id, current_user=user
    )


def update_incident(
    db: Session, user: User, incident_id: int, data: IncidentUpdate
):
    incident = incident_service.get_incident(
        db, incident_id=incident_id, current_user=user
    )
    return incident_service.update_incident(
        db, incident=incident, data=data
    )


def delete_incident(db: Session, user: User, incident_id: int):
    incident = incident_service.get_incident(
        db, incident_id=incident_id, current_user=user
    )
    incident_service.delete_incident(db, incident=incident)


def add_event(db: Session, user: User, incident_id: int, data):
    incident = incident_service.get_incident(
        db, incident_id=incident_id, current_user=user
    )
    return incident_service.add_event(db, incident=incident, data=data)


def list_events(db: Session, user: User, incident_id: int):
    incident = incident_service.get_incident(
        db, incident_id=incident_id, current_user=user
    )
    return incident_service.get_events(db, incident=incident)