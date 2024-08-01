from fastapi.testclient import TestClient
from fastapi import status
from TodoApp import application

client = TestClient(application.app)


def test_application_health_check_returns_healthy_status():
    response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'Healthy'}
