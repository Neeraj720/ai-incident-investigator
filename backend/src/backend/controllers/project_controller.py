from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models.user import User
from backend.schemas.project import ProjectCreate, ProjectUpdate
from backend.services import project_service


def create_project(
    db: Session,
    current_user: User,
    data: ProjectCreate,
):
    return project_service.create_project(
        db,
        data=data,
        owner_id=current_user.id,
    )


def list_projects(db: Session, current_user: User):
    return project_service.list_projects(
        db,
        owner_id=current_user.id,
    )


def get_project(db: Session, current_user: User, project_id: int):
    return project_service.get_project_or_raise(
        db,
        project_id=project_id,
        owner_id=current_user.id,
    )


def update_project(
    db: Session,
    current_user: User,
    project_id: int,
    data: ProjectUpdate,
):
    project = project_service.get_project_or_raise(
        db,
        project_id=project_id,
        owner_id=current_user.id,
    )

    return project_service.update_project(
        db,
        project=project,
        data=data,
    )


def delete_project(db: Session, current_user: User, project_id: int):
    project = project_service.get_project_or_raise(
        db,
        project_id=project_id,
        owner_id=current_user.id,
    )

    project_service.delete_project(db, project=project)

    return None