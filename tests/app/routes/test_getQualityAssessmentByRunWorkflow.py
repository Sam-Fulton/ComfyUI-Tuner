import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes.getQualityAssessmentByRunWorkflow import get_quality_assessment_by_run_workflow_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(get_quality_assessment_by_run_workflow_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.routes.getQualityAssessmentByRunWorkflow.get_db')
@patch('app.routes.getQualityAssessmentByRunWorkflow.find_quality_assessments_by_run_workflow_ids')
def test_get_quality_assessment_by_run_workflow(mock_find_quality_assessments, mock_get_db, client):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_find_quality_assessments.return_value = [
        {"run_workflow_id": "mocked_id_1", "quality_assessment": "good"},
        {"run_workflow_id": "mocked_id_2", "quality_assessment": "bad"}
    ]

    response = client.post('/api/getQualityAssessmentByRunWorkflow', json={
        "run_workflow_ids": ["mocked_id_1", "mocked_id_2"]
    })

    assert response.status_code == 200
    json_data = response.get_json()
    assert "quality_assessments" in json_data
    assert len(json_data["quality_assessments"]) == 2

@patch('app.routes.getQualityAssessmentByRunWorkflow.get_db')
@patch('app.routes.getQualityAssessmentByRunWorkflow.find_quality_assessments_by_run_workflow_ids')
def test_get_quality_assessment_by_run_workflow_missing_ids(mock_find_quality_assessments, mock_get_db, client):
    response = client.post('/api/getQualityAssessmentByRunWorkflow', json={})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data == {"error": "No valid run_workflow_id was supplied"}

@patch('app.routes.getQualityAssessmentByRunWorkflow.get_db')
@patch('app.routes.getQualityAssessmentByRunWorkflow.find_quality_assessments_by_run_workflow_ids')
def test_get_quality_assessment_by_run_workflow_invalid_json(mock_find_quality_assessments, mock_get_db, client):
    response = client.post('/api/getQualityAssessmentByRunWorkflow', data="Invalid JSON", content_type='application/json')
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data == {"error": "No valid json data was supplied"}

@patch('app.routes.getQualityAssessmentByRunWorkflow.get_db')
@patch('app.routes.getQualityAssessmentByRunWorkflow.find_quality_assessments_by_run_workflow_ids')
def test_get_quality_assessment_by_run_workflow_internal_error(mock_find_quality_assessments, mock_get_db, client):
    mock_find_quality_assessments.side_effect = Exception("Test Exception")

    response = client.post('/api/getQualityAssessmentByRunWorkflow', json={
        "run_workflow_ids": ["mocked_id_1"]
    })

    assert response.status_code == 500
    json_data = response.get_json()
    assert "error" in json_data
    assert json_data["error"] == "Test Exception"
