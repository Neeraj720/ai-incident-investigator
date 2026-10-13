from pydantic import BaseModel


class AtlassianImportRequest(BaseModel):
    project_id: int


class AtlassianImportResponse(BaseModel):
    incident_id: int
    external_id: str
    source: str
    event_count: int
    created: bool