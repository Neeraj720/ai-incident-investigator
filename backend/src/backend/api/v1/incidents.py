from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.controllers import incident_controller
from backend.core.dependencies import get_current_user, get_db
from backend.models.user import User
from backend.schemas.incident import (
    IncidentCreate,
    IncidentEventCreate,
    IncidentEventResponse,
    IncidentResponse,
    IncidentUpdate,
)

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("", response_model=IncidentResponse, status_code=201)
def create_incident(
    data: IncidentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return incident_controller.create_incident(db, user, data)


@router.get("", response_model=list[IncidentResponse])
def list_incidents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return incident_controller.list_incidents(db, user)


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return incident_controller.get_incident(db, user, incident_id)


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    data: IncidentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return incident_controller.update_incident(
        db, user, incident_id, data
    )


@router.delete("/{incident_id}", status_code=204)
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    incident_controller.delete_incident(db, user, incident_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{incident_id}/events",
    response_model=IncidentEventResponse,
    status_code=201,
)
def add_event(
    incident_id: int,
    data: IncidentEventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return incident_controller.add_event(db, user, incident_id, data)


@router.get(
    "/{incident_id}/events",
    response_model=list[IncidentEventResponse],
)
def list_events(
    incident_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return incident_controller.list_events(db, user, incident_id)