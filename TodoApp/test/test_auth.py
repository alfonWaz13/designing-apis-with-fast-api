from datetime import timedelta

import pytest
from jose import jwt
from sqlalchemy import text

from TodoApp.routers.auth import authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
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


def test_create_access_token_function_returns_a_valid_access_token():
    token = create_access_token(
        username=PREDEFINED_NON_ADMIN_USER['username'],
        user_id=PREDEFINED_NON_ADMIN_USER['id'],
        role=PREDEFINED_NON_ADMIN_USER['role'],
        delta_expiration_time=timedelta(days=1)
    )
    decoded_token = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

    assert decoded_token['sub'] == PREDEFINED_NON_ADMIN_USER['username']
    assert decoded_token['id'] == PREDEFINED_NON_ADMIN_USER['id']
    assert decoded_token['role'] == PREDEFINED_NON_ADMIN_USER['role']


@pytest.mark.asyncio
async def test_get_current_user_validates_token_correctly():
    encode = {
        'sub': PREDEFINED_NON_ADMIN_USER['username'],
        'id': PREDEFINED_NON_ADMIN_USER['id'],
        'role': PREDEFINED_NON_ADMIN_USER['role']
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token)

    assert user['username'] == PREDEFINED_NON_ADMIN_USER['username']
    assert user['id'] == PREDEFINED_NON_ADMIN_USER['id']
    assert user['role'] == PREDEFINED_NON_ADMIN_USER['role']
