import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes.getRunWorkflows import get_run_workflows_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(get_run_workflows_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.routes.getRunWorkflows.get_db')
@patch('app.routes.getRunWorkflows.fetch_run_workflows')
def test_get_run_workflows_success(mock_fetch_run_workflows, mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_fetch_run_workflows.return_value = [
        {"_id": "mocked_id_1", "value": "workflow_1"},
        {"_id": "mocked_id_2", "value": "workflow_2"}
    ]
    response = client.get('/api/getRunWorkflows')
    assert response.status_code == 200
    json_data = response.get_json()
    assert "workflows" in json_data
    assert len(json_data["workflows"]) == 2
    assert json_data["workflows"][0]["_id"] == "mocked_id_1"

@patch('app.routes.getRunWorkflows.get_db')
@patch('app.routes.getRunWorkflows.fetch_run_workflows')
def test_get_run_workflows_failure(mock_fetch_run_workflows, mock_get_db, client):
    mock_get_db.side_effect = Exception("Database connection error")
    response = client.get('/api/getRunWorkflows')
    assert response.status_code == 500
    json_data = response.get_json()
    assert "error" in json_data
    assert json_data["error"] == "Database connection error"

@patch('app.routes.getRunWorkflows.get_db')
@patch('app.routes.getRunWorkflows.fetch_run_workflows')
def test_get_run_workflows_no_data(mock_fetch_run_workflows, mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_fetch_run_workflows.return_value = []
    response = client.get('/api/getRunWorkflows')
    assert response.status_code == 200
    json_data = response.get_json()
    assert "workflows" in json_data
    assert len(json_data["workflows"]) == 0
