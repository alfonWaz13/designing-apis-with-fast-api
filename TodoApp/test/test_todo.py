import pytest
import sqlalchemy

from TodoApp.models import ToDos
from TodoApp.test.config import client, TestingSessionLocal, engine

from fastapi import status


class TestGet:

    predefined_todo = ToDos(
        title="Test",
        description="Test",
        priority=5,
        complete=False,
        owner_id=1
    )

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        db = TestingSessionLocal()
        db.add(self.predefined_todo)
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
