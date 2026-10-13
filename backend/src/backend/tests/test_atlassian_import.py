from sqlalchemy import select

from backend.integrations.atlassian_client import AtlassianClient
from backend.models.incident import Incident
from backend.models.incident_event import IncidentEvent
from backend.services.atlassian_import_service import AtlassianImportService


def test_import_real_atlassian_incident(
    db,
    user_and_project,
):
    user, project = user_and_project

    service = AtlassianImportService(
        client=AtlassianClient()
    )

    external_id = "2ypy8lwt1prw"

    result = service.import_incident(
        db,
        external_id=external_id,
        project_id=project.id,
        current_user=user,
    )

    assert result["created"] is True
    assert result["incident"].external_id == external_id
    assert result["incident"].source == "atlassian"
    assert len(result["events"]) > 0

    incident_id = result["incident"].id

    incidents = db.scalars(
        select(Incident).where(
            Incident.id == incident_id
        )
    ).all()

    events = db.scalars(
        select(IncidentEvent).where(
            IncidentEvent.incident_id == incident_id
        )
    ).all()

    assert len(incidents) == 1
    assert len(events) == len(result["events"])


def test_import_is_idempotent(
    db,
    user_and_project,
):
    user, project = user_and_project

    service = AtlassianImportService(
        client=AtlassianClient()
    )

    external_id = "2ypy8lwt1prw"

    first = service.import_incident(
        db,
        external_id=external_id,
        project_id=project.id,
        current_user=user,
    )

    second = service.import_incident(
        db,
        external_id=external_id,
        project_id=project.id,
        current_user=user,
    )

    assert first["created"] is True
    assert second["created"] is False

    incidents = db.scalars(
        select(Incident).where(
            Incident.source == "atlassian",
            Incident.external_id == external_id,
        )
    ).all()

    assert len(incidents) == 1