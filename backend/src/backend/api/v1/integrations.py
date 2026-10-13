from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.controllers import integration_controller
from backend.core.dependencies import get_current_user, get_db
from backend.models.user import User
from backend.schemas.integration import (
    AtlassianImportRequest,
    AtlassianImportResponse,
)

router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"],
)


@router.post(
    "/atlassian/incidents/{external_id}/import",
    response_model=AtlassianImportResponse,
    status_code=status.HTTP_200_OK,
)
def import_atlassian_incident(
    external_id: str,
    data: AtlassianImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = integration_controller.import_atlassian_incident(
        db,
        external_id=external_id,
        project_id=data.project_id,
        current_user=current_user,
    )

    return AtlassianImportResponse(
        incident_id=result["incident"].id,
        external_id=result["incident"].external_id,
        source=result["incident"].source,
        event_count=len(result["events"]),
        created=result["created"],
    )