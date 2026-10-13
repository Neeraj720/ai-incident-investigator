from datetime import datetime


class AtlassianNormalizer:

    SOURCE = "atlassian"

    SEVERITY_MAP = {
        "minor": "low",
        "major": "high",
        "critical": "critical",
    }

    STATUS_MAP = {
        "investigating": "investigating",
        "identified": "investigating",
        "monitoring": "investigating",
        "resolved": "resolved",
        "postmortem": "resolved",
    }

    @staticmethod
    def normalize_incident(data: dict) -> dict:
        """
        Convert an Atlassian incident into our internal incident format.
        """

        if not isinstance(data, dict):
            raise ValueError("Atlassian incident must be a dictionary")

        required_fields = [
            "id",
            "name",
            "status",
            "impact",
        ]

        for field in required_fields:
            if field not in data:
                raise ValueError(
                    f"Missing required Atlassian incident field: {field}"
                )

        impact = data["impact"]
        status = data["status"]

        severity = AtlassianNormalizer.SEVERITY_MAP.get(
            impact,
            "medium",
        )

        normalized_status = AtlassianNormalizer.STATUS_MAP.get(
            status,
            "open",
        )

        return {
            "external_id": str(data["id"]),
            "source": AtlassianNormalizer.SOURCE,
            "title": data["name"],
            "description": None,
            "status": normalized_status,
            "severity": severity,
            "started_at": AtlassianNormalizer._parse_datetime(
                data.get("started_at")
            ),
            "resolved_at": AtlassianNormalizer._parse_datetime(
                data.get("resolved_at")
            ),
            "source_url": data.get("shortlink"),
        }

    @staticmethod
    def normalize_events(data: dict) -> list[dict]:
        """
        Convert Atlassian incident updates into our internal event format.
        """

        updates = data.get("incident_updates", [])

        if not isinstance(updates, list):
            raise ValueError(
                "Atlassian incident_updates must be a list"
            )

        events = []

        for update in updates:
            if not isinstance(update, dict):
                continue

            if not update.get("id"):
                continue

            events.append(
                {
                    "external_id": str(update["id"]),
                    "source": AtlassianNormalizer.SOURCE,
                    "event_type": update.get(
                        "status",
                        "update",
                    ),
                    "message": update.get(
                        "body",
                        "Atlassian incident update",
                    ),
                    "occurred_at": AtlassianNormalizer._parse_datetime(
                        update.get("created_at")
                    ),
                    "event_metadata": {
                        "affected_components": update.get(
                            "affected_components",
                            [],
                        ),
                    },
                }
            )

        return events

    @staticmethod
    def _parse_datetime(
        value: str | None,
    ) -> datetime | None:
        """
        Convert an ISO timestamp from Atlassian into a Python datetime.
        """

        if not value:
            return None

        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )