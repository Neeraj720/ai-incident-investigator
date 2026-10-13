from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.integrations.atlassian_client import AtlassianClient
from backend.models.project import Project
from backend.models.user import User
from backend.repositories import incident_repository
from backend.services.atlassian_normalizer import AtlassianNormalizer


class AtlassianImportService:

    def __init__(self, client: AtlassianClient):
        self.client = client

    def import_incident(
        self,
        db: Session,
        *,
        external_id: str,
        project_id: int,
        current_user: User,
    ):
        # 1. Verify project ownership
        project = db.scalar(
            select(Project).where(
                Project.id == project_id,
                Project.owner_id == current_user.id,
            )
        )

        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found",
            )

        # 2. Fetch incident from Atlassian
        external_incident = self.client.get_incident(
            external_id
        )

        # 3. Normalize external data
        incident_data = AtlassianNormalizer.normalize_incident(
            external_incident
        )

        event_data = AtlassianNormalizer.normalize_events(
            external_incident
        )

        try:
            # 4. Check whether incident already exists
            incident = incident_repository.get_by_external_identity(
                db,
                source=incident_data["source"],
                external_id=incident_data["external_id"],
            )

            created = False

            # 5A. Create new incident
            if incident is None:
                incident = incident_repository.create_import_incident(
                    db,
                    data={
                        **incident_data,
                        "project_id": project.id,
                        "created_by_id": current_user.id,
                    },
                )

                created = True

            # 5B. Update existing incident
            else:
                incident = incident_repository.update_import_incident(
                    db,
                    incident=incident,
                    updates={
                        "title": incident_data["title"],
                        "description": incident_data["description"],
                        "status": incident_data["status"],
                        "severity": incident_data["severity"],
                        "started_at": incident_data["started_at"],
                        "resolved_at": incident_data["resolved_at"],
                        "source_url": incident_data["source_url"],
                    },
                )

            # 6. Create/update events
            imported_events = []

            for event_data_item in event_data:
                existing_event = (
                    incident_repository.get_event_by_external_identity(
                        db,
                        incident_id=incident.id,
                        source=event_data_item["source"],
                        external_id=event_data_item["external_id"],
                    )
                )

                # 6A. Create new event
                if existing_event is None:
                    event = incident_repository.create_import_event(
                        db,
                        incident_id=incident.id,
                        data=event_data_item,
                    )

                # 6B. Update existing event
                else:
                    event = incident_repository.update_import_event(
                        db,
                        event=existing_event,
                        updates={
                            "event_type": event_data_item["event_type"],
                            "message": event_data_item["message"],
                            "occurred_at": event_data_item["occurred_at"],
                            "event_metadata": event_data_item[
                                "event_metadata"
                            ],
                        },
                    )

                imported_events.append(event)

            # 7. ONE commit for the entire import
            db.commit()

            return {
                "incident": incident,
                "events": imported_events,
                "created": created,
            }

        except Exception:
            # Any failure means everything is rolled back.
            db.rollback()
            raise