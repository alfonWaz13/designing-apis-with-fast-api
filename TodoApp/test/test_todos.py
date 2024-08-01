import sqlalchemy

from TodoApp.database import Base, get_database
from TodoApp.application import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = sqlalchemy.create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=sqlalchemy.StaticPool
)

TestingSessionLocal = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_database():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_database] = override_get_database
