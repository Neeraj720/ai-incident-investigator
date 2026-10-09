from sqlalchemy.orm import Session

from backend.models.project import Project
from backend.repositories import project_repository
from backend.schemas.project import ProjectCreate, ProjectUpdate


def create_project(
    db: Session,
    *,
    data: ProjectCreate,
    owner_id: int,
) -> Project:
    return project_repository.create_project(
        db,
        name=data.name,
        description=data.description,
        owner_id=owner_id,
    )


def list_projects(db: Session, *, owner_id: int) -> list[Project]:
    return project_repository.list_projects(db, owner_id=owner_id)


def get_project_or_raise(
    db: Session,
    *,
    project_id: int,
    owner_id: int,
) -> Project:
    project = project_repository.get_project(
        db,
        project_id=project_id,
        owner_id=owner_id,
    )

    if project is None:
        # Don't disclose whether another user's project exists.
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


def update_project(
    db: Session,
    *,
    project: Project,
    data: ProjectUpdate,
) -> Project:
    updates = data.model_dump(exclude_unset=True)

    return project_repository.update_project(
        db,
        project=project,
        updates=updates,
    )


def delete_project(db: Session, *, project: Project) -> None:
    project_repository.delete_project(db, project=project)