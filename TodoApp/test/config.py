import sqlalchemy
from sqlalchemy import text

from TodoApp.database import Base, get_database
from TodoApp.application import app
from TodoApp.routers.auth import get_current_user

from fastapi.testclient import TestClient

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = sqlalchemy.create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=sqlalchemy.StaticPool
)

Base.metadata.create_all(bind=engine)

TestingSessionLocal = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_database():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username': 'usertest', 'id': 1, 'role': 'admin'}


app.dependency_overrides[get_database] = override_get_database
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)
PREDEFINED_TODO = {
    "title": "Test",
    "description": "Test",
    "priority": 5,
    "complete": False,
    "owner_id": 1
}
INSERT_TODO_QUERY = text(
    """
    INSERT INTO todos (title, description, priority, complete, owner_id)
    VALUES (:title, :description, :priority, :complete, :owner_id)
    """
)
