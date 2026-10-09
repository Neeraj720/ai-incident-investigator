from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.incident import Incident
from backend.models.project import Project
from backend.models.service import Service
from backend.models.user import User
from backend.repositories import incident_repository
from backend.schemas.incident import IncidentCreate, IncidentUpdate


def _get_owned_project(
    db: Session, *, project_id: int, user_id: int
) -> Project:
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == user_id,
        )
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_owned_incident(
    db: Session, *, incident_id: int, user_id: int
) -> Incident:
    incident = db.scalar(
        select(Incident)
        .join(Project, Incident.project_id == Project.id)
        .where(
            Incident.id == incident_id,
            Project.owner_id == user_id,
        )
    )
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


def create_incident(
    db: Session, *, data: IncidentCreate, current_user: User
) -> Incident:
    _get_owned_project(
        db, project_id=data.project_id, user_id=current_user.id
    )

    if data.service_id is not None:
        service = db.scalar(
            select(Service).where(
                Service.id == data.service_id,
                Service.project_id == data.project_id,
            )
        )
        if service is None:
            raise HTTPException(
                status_code=422,
                detail="Service does not belong to the selected project",
            )

    return incident_repository.create_incident(
        db,
        data={
            "title": data.title,
            "description": data.description,
            "project_id": data.project_id,
            "service_id": data.service_id,
            "severity": data.severity,
            "created_by_id": current_user.id,
        },
    )


def list_incidents(db: Session, *, current_user: User) -> list[Incident]:
    project_ids = list(
        db.scalars(
            select(Project.id).where(Project.owner_id == current_user.id)
        ).all()
    )
    if not project_ids:
        return []
    return incident_repository.list_incidents(
        db, project_ids=project_ids
    )


def get_incident(
    db: Session, *, incident_id: int, current_user: User
) -> Incident:
    return _get_owned_incident(
        db, incident_id=incident_id, user_id=current_user.id
    )


def update_incident(
    db: Session,
    *,
    incident: Incident,
    data: IncidentUpdate,
) -> Incident:
    updates = data.model_dump(exclude_unset=True)

    # Record the first time the incident reaches a terminal state.
    if updates.get("status") in {"resolved", "closed"}:
        if incident.resolved_at is None:
            updates["resolved_at"] = datetime.now(timezone.utc)

    # Reopening clears the resolution timestamp.
    if updates.get("status") in {"open", "investigating"}:
        updates["resolved_at"] = None

    return incident_repository.update_incident(
        db, incident=incident, updates=updates
    )


def delete_incident(db: Session, *, incident: Incident) -> None:
    incident_repository.delete_incident(db, incident=incident)


def add_event(
    db: Session, *, incident: Incident, data
):
    payload = data.model_dump(exclude={"occurred_at"})
    if data.occurred_at is not None:
        payload["occurred_at"] = data.occurred_at

    return incident_repository.create_event(
        db, incident_id=incident.id, data=payload
    )


def get_events(db: Session, *, incident: Incident):
    return incident_repository.list_events(
        db, incident_id=incident.id
    )