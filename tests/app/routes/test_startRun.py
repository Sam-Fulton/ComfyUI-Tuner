import pytest
from flask import Flask, jsonify
from unittest.mock import patch
from datetime import datetime
from app.routes.startRun import start_run_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(start_run_bp)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_datetime():
    with patch('app.routes.startRun.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 1, 1)
        yield mock_datetime

@patch('app.routes.startRun.extract_and_validate_json')
@patch('app.routes.startRun.get_db')
@patch('app.routes.startRun.handle_base_workflow')
@patch('app.routes.startRun.prepare_workflows')
@patch('app.routes.startRun.process_run_workflow')
def test_start_run_success(mock_process_run_workflow, mock_prepare_workflows, mock_handle_base_workflow, mock_get_db, mock_extract_and_validate_json, client, mock_datetime):
    mock_extract_and_validate_json.return_value = ({"base_workflow": "data", "num_runs": 1}, None, None)
    mock_handle_base_workflow.return_value = ("processed_base_workflow", None, None)
    mock_prepare_workflows.return_value = ["run_workflow"]
    mock_process_run_workflow.return_value = ({"run_workflow_id": "run_workflow_id", "output_id": "output_id"}, None, None)
    
    response = client.post('/api/startRun', json={"base_workflow": "data", "num_runs": 1})
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["message"] == "Workflows processed successfully"
    assert len(json_data["results"]) == 1
    assert json_data["results"][0] == {"run_workflow_id": "run_workflow_id", "output_id": "output_id"}

def test_start_run_invalid_json(app, client):
    with app.app_context():
        with patch('app.routes.startRun.extract_and_validate_json', return_value=(None, jsonify({"error": "Failed to parse JSON data"}), 400)):
            response = client.post('/api/startRun', data="Invalid JSON", content_type='application/json')
            
            assert response.status_code == 400
            json_data = response.get_json()
            assert json_data["error"] == "Failed to parse JSON data"

def test_start_run_base_workflow_missing(app, client):
    with app.app_context():
        with patch('app.routes.startRun.extract_and_validate_json', return_value=({"num_runs": 1}, None, None)), \
             patch('app.routes.startRun.handle_base_workflow', return_value=(None, jsonify({"error": "Base workflow is missing"}), 400)):
            response = client.post('/api/startRun', json={"num_runs": 1})
            
            assert response.status_code == 400
            json_data = response.get_json()
            assert json_data["error"] == "Base workflow is missing"

def test_start_run_num_runs_zero(app, client):
    with app.app_context():
        with patch('app.routes.startRun.extract_and_validate_json', return_value=({"base_workflow": "data"}, None, None)):
            response = client.post('/api/startRun', json={"base_workflow": "data", "num_runs": 0})
            
            assert response.status_code == 400
            json_data = response.get_json()
            assert json_data["error"] == "Number of runs must be greater than zero"
