import pytest
from sqlalchemy import text
from fastapi import status

from TodoApp.models import ToDos
from TodoApp.routers import response_messages
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
    """Test are configured with a username with admin role"""
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    todo_stored = response.json()[0]
    assert todo_stored.get('id') == 1
    assert todo_stored.get('title') == "Test"
    assert todo_stored.get('description') == "Test"
    assert todo_stored.get('priority') == 5
    assert todo_stored.get('complete') is False
    assert todo_stored.get('owner_id') == 1


def test_delete_todo_returns_no_content_status_code():
    response = client.delete("/admin/todo/1")
    assert response.status_code == 204


def test_delete_todo_deletes_todo_from_database():
    client.delete("/admin/todo/1")
    db = TestingSessionLocal()
    model = db.query(ToDos).filter(ToDos.id == 1).first()
    assert model is None


def test_delete_todo_returns_not_found_if_the_todo_does_not_exist():
    response = client.delete('/admin/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': response_messages.ITEM_NOT_FOUND_MESSAGE}
