import pytest
from sqlalchemy import text

from TodoApp.routers.auth import authenticate_user
from TodoApp.test.config import TestingSessionLocal, PREDEFINED_NON_ADMIN_USER, NON_ADMIN_PASSWORD, engine, \
    INSERT_USER_QUERY


@pytest.fixture(autouse=True)
def setup_and_teardown():
    connection = engine.connect()
    session = TestingSessionLocal(bind=connection)

    session.execute(text("DELETE FROM todos;"))
    session.execute(text("DELETE FROM users;"))
    session.commit()
    session.execute(INSERT_USER_QUERY, PREDEFINED_NON_ADMIN_USER)
    session.commit()

    yield session

    session.execute(text("DELETE FROM todos;"))
    session.execute(text("DELETE FROM users;"))
    session.commit()
    session.close()
    connection.close()


def test_authenticate_user_returns_user_when_passing_username_and_password():
    db = TestingSessionLocal()
    username = PREDEFINED_NON_ADMIN_USER['username']
    authenticated_user = authenticate_user(username=username, password=NON_ADMIN_PASSWORD, db=db)
    assert authenticated_user
    assert authenticated_user.username == username


def test_authenticate_user_returns_none_when_passing_wrong_username():
    db = TestingSessionLocal()
    username = "WrongUsername"
    authenticated_user = authenticate_user(username=username, password='password', db=db)
    assert not authenticated_user


def test_authenticate_user_returns_none_when_passing_wrong_password():
    db = TestingSessionLocal()
    username = PREDEFINED_NON_ADMIN_USER['username']
    authenticated_user = authenticate_user(username=username, password='WrongPassword', db=db)
    assert not authenticated_user
