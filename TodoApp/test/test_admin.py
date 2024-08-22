import pytest
from sqlalchemy import text
from fastapi import status

from TodoApp.test.config import engine, TestingSessionLocal, INSERT_TODO_QUERY, PREDEFINED_TODO, client


@pytest.fixture(autouse=True)
def setup_and_teardown():
    connection = engine.connect()
    session = TestingSessionLocal(bind=connection)

    session.execute(text("DELETE FROM todos;"))
    session.commit()
    session.execute(INSERT_TODO_QUERY, PREDEFINED_TODO)
    session.commit()

    yield session

    session.execute(text("DELETE FROM todos;"))
    session.commit()
    session.close()
    connection.close()


def test_admin_reads_all_todos():
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    todo_stored = response.json()[0]
    assert todo_stored.get('id') == 1
    assert todo_stored.get('title') == "Test"
    assert todo_stored.get('description') == "Test"
    assert todo_stored.get('priority') == 5
    assert todo_stored.get('complete') is False
    assert todo_stored.get('owner_id') == 1
