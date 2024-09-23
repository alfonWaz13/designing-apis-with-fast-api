import pytest
from sqlalchemy import text

from TodoApp.routers.auth import get_current_user
from TodoApp.test.config import client, engine, TestingSessionLocal, INSERT_TODO_QUERY, PREDEFINED_TODO, \
    INSERT_USER_QUERY, PREDEFINED_ADMIN_USER, PREDEFINED_NON_ADMIN_USER
from fastapi import status


@pytest.fixture(autouse=True)
def setup_and_teardown():
    connection = engine.connect()
    session = TestingSessionLocal(bind=connection)

    session.execute(text("DELETE FROM todos;"))
    session.execute(text("DELETE FROM users;"))
    session.commit()
    session.execute(INSERT_TODO_QUERY, PREDEFINED_TODO)
    session.execute(INSERT_USER_QUERY, PREDEFINED_ADMIN_USER)
    session.execute(INSERT_USER_QUERY, PREDEFINED_NON_ADMIN_USER)
    session.commit()

    yield session

    session.execute(text("DELETE FROM todos;"))
    session.execute(text("DELETE FROM users;"))
    session.commit()
    session.close()
    connection.close()


def test_user_is_found_in_database():
    client.app.dependency_overrides[get_current_user] = lambda: PREDEFINED_NON_ADMIN_USER  # get_current_user is used for authentication
    response_json = client.get("/user")
    assert response_json.status_code == status.HTTP_200_OK

    response_json = response_json.json()
    assert response_json['username'] == PREDEFINED_NON_ADMIN_USER['username']
    assert response_json['email'] == PREDEFINED_NON_ADMIN_USER['email']
    assert response_json['first_name'] == PREDEFINED_NON_ADMIN_USER['first_name']
    assert response_json['last_name'] == PREDEFINED_NON_ADMIN_USER['last_name']
    assert response_json['role'] == PREDEFINED_NON_ADMIN_USER['role']
