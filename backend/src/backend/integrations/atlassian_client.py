import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class AtlassianAPIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class AtlassianClient:
    BASE_URL = "https://developer.status.atlassian.com/api/v2"

    def _get(self, path: str):
        url = f"{self.BASE_URL}{path}"

        headers = {
            "Accept": "application/json",
            "User-Agent": "ai-production-incident-investigator",
        }

        request = Request(
            url,
            headers=headers,
            method="GET",
        )

        try:
            with urlopen(request, timeout=15) as response:
                return json.loads(
                    response.read().decode("utf-8")
                )

        except HTTPError as exc:
            if exc.code == 404:
                message = "Atlassian incident not found"
            elif exc.code == 429:
                message = "Atlassian API rate limit exceeded"
            elif exc.code >= 500:
                message = "Atlassian Status API is unavailable"
            else:
                message = f"Atlassian API returned HTTP {exc.code}"

            raise AtlassianAPIError(
                exc.code,
                message,
            ) from exc

        except (URLError, TimeoutError) as exc:
            raise AtlassianAPIError(
                503,
                "Unable to reach Atlassian Status API",
            ) from exc

    def get_incident(self, incident_id: str) -> dict:
        """
        Fetch a single incident from the Atlassian Status API.
        """

        if not incident_id.strip():
            raise ValueError("Incident ID is required")

        path = f"/incidents/{quote(incident_id, safe='')}"

        data = self._get(path)

        if not isinstance(data, dict):
            raise AtlassianAPIError(
                502,
                "Invalid response from Atlassian Status API",
            )

        incident = data.get("incident")

        if not isinstance(incident, dict):
            raise AtlassianAPIError(
                502,
                "Invalid incident response from Atlassian Status API",
            )

        return incident

    def list_incidents(self) -> list[dict]:
        """
        Fetch incidents from the Atlassian Status API.
        """

        data = self._get("/incidents.json")

        if not isinstance(data, dict):
            raise AtlassianAPIError(
                502,
                "Invalid response from Atlassian Status API",
            )

        incidents = data.get("incidents", [])

        if not isinstance(incidents, list):
            raise AtlassianAPIError(
                502,
                "Invalid incidents response from Atlassian Status API",
            )

        return incidents