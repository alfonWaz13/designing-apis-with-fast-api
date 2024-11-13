import pytest
from sqlalchemy import text

from TodoApp.models import ToDos
from TodoApp.test.config import client, TestingSessionLocal, engine, PREDEFINED_TODO, INSERT_TODO_QUERY
from TodoApp.routers import response_messages
from TodoApp.routers.todos import PREFIX as ROUTER_PREFIX

from fastapi import status


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


class TestGet:

    def test_read_all_todos_return_pre_defined_todo(self):
        response = client.get(f"{ROUTER_PREFIX}/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0].get('id') == 1

    def test_read_todo_with_id_1_returns_the_predefined_todo(self):
        response = client.get(f"{ROUTER_PREFIX}/todo/1")
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get('id') == 1
        assert response.json().get('title') == "Test"
        assert response.json().get('description') == "Test"
        assert response.json().get('priority') == 5
        assert response.json().get('complete') is False
        assert response.json().get('owner_id') == 1

    def test_read_todo_with_id_999_returns_404_status_code(self):
        response = client.get(f"{ROUTER_PREFIX}/todo/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': response_messages.ITEM_NOT_FOUND_MESSAGE}


class TestPost:

    def test_create_todo_returns_created_status_code(self):
        request_data = {
            'title': 'test_create',
            'description': 'test_create',
            'priority': 1,
            'complete': False
        }

        response = client.post(f'{ROUTER_PREFIX}/todo/', json=request_data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_todo_stores_todo_in_database(self):
        request_data = {
            'title': 'test_create',
            'description': 'test_create',
            'priority': 1,
            'complete': False
        }

        client.post(f'{ROUTER_PREFIX}/todo/', json=request_data)
        db = TestingSessionLocal()
        model = db.query(ToDos).filter(ToDos.id == 2).first()

        assert model.title == request_data.get('title')
        assert model.description == request_data.get('description')
        assert model.priority == request_data.get('priority')
        assert model.complete == request_data.get('complete')


class TestPut:

    def test_update_todo_returns_no_content_status_code(self):
        request_data = {
            'title': 'updating todo',
            'description': 'updating todo',
            'priority': 5,
            'complete': False
        }

        response = client.put(f'{ROUTER_PREFIX}/todo/1', json=request_data)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_update_todo_updates_todo_information_in_database(self):
        request_data = {
            'title': 'updating todo',
            'description': 'updating todo',
            'priority': 5,
            'complete': False
        }

        client.put(f'{ROUTER_PREFIX}/todo/1', json=request_data)
        db = TestingSessionLocal()
        model = db.query(ToDos).filter(ToDos.id == 1).first()

        assert model.title == 'updating todo'
        assert model.description == 'updating todo'

    def test_update_todo_returns_not_found_status_code_for_an_id_that_does_not_exist_in_database(self):
        request_data = {
            'title': 'updating todo',
            'description': 'updating todo',
            'priority': 5,
            'complete': False
        }

        response = client.put(f'{ROUTER_PREFIX}/todo/999', json=request_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': response_messages.ITEM_NOT_FOUND_MESSAGE}


class TestDelete:

    def test_delete_todo_returns_no_content_status_code(self):
        response = client.delete(f'{ROUTER_PREFIX}/todo/1')
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_todo_deletes_todo_from_database(self):
        client.delete(f'{ROUTER_PREFIX}/todo/1')
        db = TestingSessionLocal()
        model = db.query(ToDos).filter(ToDos.id == 1).first()
        assert model is None

    def test_delete_todo_returns_not_found_status_code_for_an_id_that_does_not_exist_in_database(self):
        response = client.delete(f'{ROUTER_PREFIX}/todo/999')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': response_messages.ITEM_NOT_FOUND_MESSAGE}
