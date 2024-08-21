import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app.routes.uploadWorkflow import upload_workflow_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(upload_workflow_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.routes.uploadWorkflow.get_db')
@patch('app.routes.uploadWorkflow.insert_base_workflow')
def test_upload_workflow_success(mock_insert_base_workflow, mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_insert_base_workflow.return_value = None
    
    response = client.post('/api/uploadWorkflow', json={"some": "workflow_data"})
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert "message" in json_data
    assert json_data["message"] == "Workflow successfully added"

@patch('app.routes.uploadWorkflow.get_db')
@patch('app.routes.uploadWorkflow.insert_base_workflow')
def test_upload_workflow_invalid_json(mock_insert_base_workflow, mock_get_db, client):
    response = client.post('/api/uploadWorkflow', data="Invalid JSON", content_type='application/json')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data == {'error': 'Failed to parse JSON data'}

@patch('app.routes.uploadWorkflow.get_db')
@patch('app.routes.uploadWorkflow.insert_base_workflow')
def test_upload_workflow_json_is_none(mock_insert_base_workflow, mock_get_db, client):
    response = client.post('/api/uploadWorkflow', json=None)
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data == {'error': 'Failed to parse JSON data'}

@patch('app.routes.uploadWorkflow.get_db')
@patch('app.routes.uploadWorkflow.insert_base_workflow')
def test_upload_workflow_internal_server_error(mock_insert_base_workflow, mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_insert_base_workflow.side_effect = Exception("Some unexpected error")
    
    response = client.post('/api/uploadWorkflow', json={"some": "workflow_data"})
    
    assert response.status_code == 500
    json_data = response.get_json()
    assert "error" in json_data
    assert json_data["error"] == "Failed to insert workflow into database: Some unexpected error"
