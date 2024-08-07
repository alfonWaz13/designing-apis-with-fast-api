import pytest
import sqlalchemy

from TodoApp.models import ToDos
from TodoApp.test.config import client, TestingSessionLocal, engine
from TodoApp.routers import response_messages

from fastapi import status


PREDEFINED_TODO = ToDos(
        title="Test",
        description="Test",
        priority=5,
        complete=False,
        owner_id=1
    )


class TestGet:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        db = TestingSessionLocal()
        db.add(PREDEFINED_TODO)
        db.commit()
        db.close()
        yield
        with engine.connect() as connection:
            connection.execute(sqlalchemy.text("DELETE FROM todos;"))
            connection.commit()

    def test_read_all_todos_return_pre_defined_todo(self):
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0].get('id') == 1

    def test_read_todo_with_id_1_returns_the_predefined_todo(self):
        response = client.get("/todo/1")
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get('id') == 1
        assert response.json().get('title') == "Test"
        assert response.json().get('description') == "Test"
        assert response.json().get('priority') == 5
        assert response.json().get('complete') is False
        assert response.json().get('owner_id') == 1

    def test_read_todo_with_id_999_returns_404_status_code(self):
        response = client.get("/todo/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': response_messages.ITEM_NOT_FOUND_MESSAGE}
