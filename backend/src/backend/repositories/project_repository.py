from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.project import Project


def create_project(
    db: Session,
    *,
    name: str,
    description: str | None,
    owner_id: int,
) -> Project:
    project = Project(
        name=name,
        description=description,
        owner_id=owner_id,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def list_projects(db: Session, *, owner_id: int) -> list[Project]:
    statement = (
        select(Project)
        .where(Project.owner_id == owner_id)
        .order_by(Project.id.desc())
    )

    return list(db.scalars(statement).all())


def get_project(
    db: Session,
    *,
    project_id: int,
    owner_id: int,
) -> Project | None:
    statement = select(Project).where(
        Project.id == project_id,
        Project.owner_id == owner_id,
    )

    return db.scalar(statement)


def update_project(
    db: Session,
    *,
    project: Project,
    updates: dict,
) -> Project:
    for field, value in updates.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    return project


def delete_project(db: Session, *, project: Project) -> None:
    db.delete(project)
    db.commit()