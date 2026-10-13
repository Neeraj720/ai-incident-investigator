import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.main import app
from backend.db.database import Base
from backend.core.config import settings

# Import all models so they are registered in Base.metadata
import backend.models.user
import backend.models.project
import backend.models.service
import backend.models.incident
import backend.models.incident_event


TEST_DATABASE_URL = (
    settings.database_url.rsplit("/", 1)[0]
    + "/incident_test_db"
)

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def user_and_project(db):
    from backend.models.user import User
    from backend.models.project import Project

    user = User(
        email="day6-test@example.com",
        password_hash="test-password",
        role="engineer",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    project = Project(
        name="Day 6 Test Project",
        description="Integration test project",
        owner_id=user.id,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return user, project