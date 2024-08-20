import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes.getRunWorkflowsByBaseID import get_run_workflows_by_base_id_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(get_run_workflows_by_base_id_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('app.routes.getRunWorkflowsByBaseID.get_db')
@patch('app.routes.getRunWorkflowsByBaseID.fetch_run_workflows_by_base_workflow_id')
def test_get_run_workflows_by_base_id_success(mock_fetch_run_workflows, mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_fetch_run_workflows.return_value = [
        {"_id": "mocked_run_workflow_id_1", "value": "run_workflow_1"},
        {"_id": "mocked_run_workflow_id_2", "value": "run_workflow_2"}
    ]
    
    response = client.post('/api/getRunWorkflowsByBaseID', json={"base_workflow_id": "mocked_base_workflow_id"})
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert "run_workflows" in json_data
    assert len(json_data["run_workflows"]) == 2
    assert json_data["run_workflows"][0]["_id"] == "mocked_run_workflow_id_1"

@patch('app.routes.getRunWorkflowsByBaseID.get_db')
@patch('app.routes.getRunWorkflowsByBaseID.fetch_run_workflows_by_base_workflow_id')
def test_get_run_workflows_by_base_id_failure(mock_fetch_run_workflows, mock_get_db, client):
    mock_get_db.side_effect = Exception("Database connection error")
    
    response = client.post('/api/getRunWorkflowsByBaseID', json={"base_workflow_id": "mocked_base_workflow_id"})
    
    assert response.status_code == 500
    json_data = response.get_json()
    assert "error" in json_data
    assert json_data["error"] == "Database connection error"

@patch('app.routes.getRunWorkflowsByBaseID.get_db')
@patch('app.routes.getRunWorkflowsByBaseID.fetch_run_workflows_by_base_workflow_id')
def test_get_run_workflows_by_base_id_no_data(mock_fetch_run_workflows, mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_fetch_run_workflows.return_value = []
    
    response = client.post('/api/getRunWorkflowsByBaseID', json={"base_workflow_id": "mocked_base_workflow_id"})
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert "run_workflows" in json_data
    assert len(json_data["run_workflows"]) == 0
