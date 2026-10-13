from sqlalchemy.orm import Session

from backend.models.user import User
from backend.services.atlassian_import_service import AtlassianImportService
from backend.integrations.atlassian_client import AtlassianClient


def import_atlassian_incident(
    db: Session,
    *,
    external_id: str,
    project_id: int,
    current_user: User,
):
    service = AtlassianImportService(
        client=AtlassianClient()
    )

    return service.import_incident(
        db,
        external_id=external_id,
        project_id=project_id,
        current_user=current_user,
    )