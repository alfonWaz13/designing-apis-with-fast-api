import pytest
from sqlalchemy import text

from TodoApp.routers.auth import get_current_user
from TodoApp.test.config import client, engine, TestingSessionLocal, INSERT_TODO_QUERY, PREDEFINED_TODO, \
    INSERT_USER_QUERY, PREDEFINED_ADMIN_USER, PREDEFINED_NON_ADMIN_USER, NON_ADMIN_PASSWORD
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


@pytest.mark.parametrize("current_password, expected_status_code",
                         [(NON_ADMIN_PASSWORD, status.HTTP_204_NO_CONTENT),
                          ('incorrect_password', status.HTTP_401_UNAUTHORIZED)])
def test_password_success_only_when_correct_password_is_provided(current_password, expected_status_code):

    client.app.dependency_overrides[get_current_user] = lambda: PREDEFINED_NON_ADMIN_USER
    response = client.put("/user/password", json={"current_password": current_password, "new_password": "newpassword"})
    assert response.status_code == expected_status_code
