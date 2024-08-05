import pytest
import sqlalchemy

from TodoApp.models import ToDos
from TodoApp.test.config import client, TestingSessionLocal, engine



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

