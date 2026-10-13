
import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


class GitHubAPIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None):
        self.token = token

    def _get(self, path: str, params: dict | None = None):
        url = f"{self.BASE_URL}{path}"

        if params:
            url = f"{url}?{urlencode(params)}"

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ai-production-incident-investigator",
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        request = Request(url, headers=headers, method="GET")

        try:
            with urlopen(request, timeout=15) as response:
                return json.loads(response.read().decode("utf-8"))

        except HTTPError as exc:
            # Don't expose credentials or raw request headers.
            if exc.code == 404:
                message = "Repository or resource not found"
            elif exc.code == 401:
                message = "GitHub authentication failed"
            elif exc.code == 403:
                message = "GitHub access denied or rate limit exceeded"
            else:
                message = f"GitHub API returned HTTP {exc.code}"

            raise GitHubAPIError(exc.code, message) from exc

        except (URLError, TimeoutError) as exc:
            raise GitHubAPIError(
                503, "Unable to reach GitHub API"
            ) from exc

    @staticmethod
    def _validate_repository(owner: str, repo: str):
        if not owner.strip() or not repo.strip():
            raise ValueError("Owner and repository are required")

    def list_commits(
        self,
        owner: str,
        repo: str,
        per_page: int = 20,
    ) -> list[dict]:
        self._validate_repository(owner, repo)

        if not 1 <= per_page <= 100:
            raise ValueError("per_page must be between 1 and 100")

        path = (
            f"/repos/{quote(owner, safe='')}/"
            f"{quote(repo, safe='')}/commits"
        )

        return self._get(path, {"per_page": per_page})

    def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        per_page: int = 20,
    ) -> list[dict]:
        self._validate_repository(owner, repo)

        if state not in {"open", "closed", "all"}:
            raise ValueError("state must be open, closed or all")

        if not 1 <= per_page <= 100:
            raise ValueError("per_page must be between 1 and 100")

        path = (
            f"/repos/{quote(owner, safe='')}/"
            f"{quote(repo, safe='')}/pulls"
        )

        return self._get(
            path,
            {"state": state, "per_page": per_page},
        )
