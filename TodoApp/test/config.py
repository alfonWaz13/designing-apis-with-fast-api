import sqlalchemy
from sqlalchemy import text

from TodoApp.database import Base, get_database
from TodoApp.application import app
from TodoApp.routers.auth import get_current_user, bcrypt_context

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


app.dependency_overrides[get_database] = override_get_database
app.dependency_overrides[get_current_user] = lambda: {'username': 'usertest', 'id': 1, 'role': 'admin'}

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

ADMIN_PASSWORD = 'admin_password'
PREDEFINED_ADMIN_USER = {'id': 1, 'email': 'admin@example.com', 'username': 'useradmin', 'first_name': 'Admin',
                         'last_name': 'User', 'hashed_password': bcrypt_context.hash(ADMIN_PASSWORD), 'is_active': True,
                         'role': 'admin'}
NON_ADMIN_PASSWORD = 'non_admin_password'
PREDEFINED_NON_ADMIN_USER = {'id': 2, 'email': 'user@example.com', 'username': 'user', 'first_name': 'Regular',
                             'last_name': 'User', 'hashed_password': bcrypt_context.hash(NON_ADMIN_PASSWORD),
                             'is_active': True, 'role': 'owner'}
INSERT_USER_QUERY = text(
    """
    INSERT INTO users (id, email, username, first_name, last_name, hashed_password, is_active, role)
    VALUES (:id, :email, :username, :first_name, :last_name, :hashed_password, :is_active, :role)
    """
)

