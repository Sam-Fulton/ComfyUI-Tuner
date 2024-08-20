import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes.getOutputs import get_outputs_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(get_outputs_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.routes.getOutputs.find_run_workflow')
@patch('app.routes.getOutputs.find_outputs_by_run_workflow_id')
@patch('app.routes.getOutputs.get_db')
def test_get_outputs_success(mock_get_db, mock_find_outputs_by_run_workflow_id, mock_find_run_workflow, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    mock_find_run_workflow.return_value = {"key": "value"}
    mock_find_outputs_by_run_workflow_id.return_value = [{"path": "/some/path"}]

    response = client.post('/api/getOutputs', json={"run_workflow_id": "mocked_id"})
    
    assert response.status_code == 200
    assert response.json == {
        "message": "Outputs for run mocked_id retrieved",
        "outputs": [{"path": "/some/path"}]
    }

@patch('app.routes.getOutputs.find_run_workflow')
@patch('app.routes.getOutputs.get_db')
def test_get_outputs_workflow_not_found(mock_get_db, mock_find_run_workflow, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    mock_find_run_workflow.return_value = None

    response = client.post('/api/getOutputs', json={"run_workflow_id": "mocked_id"})
    
    assert response.status_code == 400
    assert response.json == {"error": "There was no workflow found with id : mocked_id"}

@patch('app.routes.getOutputs.find_run_workflow')
@patch('app.routes.getOutputs.find_outputs_by_run_workflow_id')
@patch('app.routes.getOutputs.get_db')
def test_get_outputs_no_outputs_found(mock_get_db, mock_find_outputs_by_run_workflow_id, mock_find_run_workflow, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    mock_find_run_workflow.return_value = {"key": "value"}
    mock_find_outputs_by_run_workflow_id.return_value = None 

    response = client.post('/api/getOutputs', json={"run_workflow_id": "mocked_id"})
    
    assert response.status_code == 400
    assert response.json == {"error": "There was no outputs found for workflow: mocked_id"}

@patch('app.routes.getOutputs.get_db')
def test_get_outputs_exception(mock_get_db, client):
    mock_get_db.side_effect = Exception("Database connection failed")

    response = client.post('/api/getOutputs', json={"run_workflow_id": "mocked_id"})
    
    assert response.status_code == 500
    assert response.json == {"error": "Database connection failed"}
