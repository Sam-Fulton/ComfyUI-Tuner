import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app.routes.rerun import rerun_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(rerun_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.routes.rerun.get_db')
@patch('app.routes.rerun.find_base_workflow')
@patch('app.routes.rerun.update_ranges_by_quality_control')
def test_rerun_success(mock_update_ranges, mock_find_base_workflow, mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_find_base_workflow.return_value = {"_id": "mocked_base_workflow_id", "value": "mocked_base_workflow"}
    mock_update_ranges.return_value = {"updated_key": "updated_value"}
    
    response = client.post('/api/rerun_workflow', json={
        "base_workflow_id": "mocked_base_workflow_id",
        "run_workflow_ids": ["run_id_1", "run_id_2"],
        "threshold": 0.5
    })
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert "updated_workflow" in json_data
    assert json_data["updated_workflow"] == {"updated_key": "updated_value"}

@patch('app.routes.rerun.get_db')
@patch('app.routes.rerun.find_base_workflow')
@patch('app.routes.rerun.update_ranges_by_quality_control')
def test_rerun_base_workflow_not_found(mock_update_ranges, mock_find_base_workflow, mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_find_base_workflow.return_value = None
    
    response = client.post('/api/rerun_workflow', json={
        "base_workflow_id": "non_existing_base_workflow_id",
        "run_workflow_ids": ["run_id_1", "run_id_2"],
        "threshold": 0.5
    })
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data
    assert json_data["error"] == "Base workflow not found"

@patch('app.routes.rerun.get_db')
@patch('app.routes.rerun.find_base_workflow')
@patch('app.routes.rerun.update_ranges_by_quality_control')
def test_rerun_invalid_json(mock_update_ranges, mock_find_base_workflow, mock_get_db, client):
    response = client.post('/api/rerun_workflow', data="Invalid JSON", content_type='application/json')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data == {"error": "No valid run data was supplied, please upload a workflow/prompt"}

@patch('app.routes.rerun.get_db')
@patch('app.routes.rerun.find_base_workflow')
@patch('app.routes.rerun.update_ranges_by_quality_control')
def test_rerun_internal_server_error(mock_update_ranges, mock_find_base_workflow, mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_find_base_workflow.side_effect = Exception("Some unexpected error")
    
    response = client.post('/api/rerun_workflow', json={
        "base_workflow_id": "mocked_base_workflow_id",
        "run_workflow_ids": ["run_id_1", "run_id_2"],
        "threshold": 0.5
    })
    
    assert response.status_code == 500
    json_data = response.get_json()
    assert "error" in json_data
    assert json_data["error"] == "Some unexpected error"

@patch('app.routes.rerun.get_db')
@patch('app.routes.rerun.find_base_workflow')
@patch('app.routes.rerun.update_ranges_by_quality_control')
def test_rerun_missing_required_fields(mock_update_ranges, mock_find_base_workflow, mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    
    response = client.post('/api/rerun_workflow', json={
        "run_workflow_ids": ["run_id_1", "run_id_2"],
        "threshold": 0.5
    })
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data
    assert json_data["error"] == "Missing required data in the JSON payload"

@patch('app.routes.rerun.get_db')
@patch('app.routes.rerun.find_base_workflow')
@patch('app.routes.rerun.update_ranges_by_quality_control')
def test_rerun_no_json_supplied(mock_update_ranges, mock_find_base_workflow, mock_get_db, client):
    response = client.post('/api/rerun_workflow')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data == {"error": "No valid run data was supplied, please upload a workflow/prompt"}
