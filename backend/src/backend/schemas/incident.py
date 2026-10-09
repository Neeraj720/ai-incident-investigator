from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Severity = Literal["low", "medium", "high", "critical"]
IncidentStatus = Literal["open", "investigating", "resolved", "closed"]


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    project_id: int
    service_id: int | None = None
    severity: Severity = "medium"


class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    severity: Severity | None = None
    status: IncidentStatus | None = None

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        for field in ("title", "severity", "status"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")

        return self


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str | None
    severity: str
    status: str
    project_id: int
    service_id: int | None
    created_by_id: int
    started_at: datetime
    resolved_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidentEventCreate(BaseModel):
    event_type: str = Field(min_length=2, max_length=50)
    source: str = Field(default="manual", min_length=2, max_length=50)
    message: str = Field(min_length=1, max_length=10000)
    occurred_at: datetime | None = None
    event_metadata: dict | None = None


class IncidentEventResponse(BaseModel):
    id: int
    incident_id: int
    event_type: str
    source: str
    message: str
    occurred_at: datetime
    event_metadata: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)