import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes.qualityCheck import quality_check_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(quality_check_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.routes.qualityCheck.insert_quality_review')
@patch('app.routes.qualityCheck.update_quality_assessment')
@patch('app.routes.qualityCheck.find_quality_assessments_by_run_workflow_id_path')
@patch('app.routes.qualityCheck.get_db')
@patch('app.routes.qualityCheck.QualityAssessment')
def test_quality_check_insert(mock_quality_assessment, mock_get_db, mock_find_quality_assessments, mock_update_quality_assessment, mock_insert_quality_review, client):
    mock_find_quality_assessments.return_value = []
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    
    response = client.post('/api/qualityCheck', json={
        "run_workflow_id": "mocked_id",
        "path": "/path/to/image",
        "quality_assessment": "good"
    })
    
    assert response.status_code == 200
    assert response.json == {"message": "Quality assessment for image saved"}
    mock_insert_quality_review.assert_called_once()
    mock_update_quality_assessment.assert_not_called()

@patch('app.routes.qualityCheck.insert_quality_review')
@patch('app.routes.qualityCheck.update_quality_assessment')
@patch('app.routes.qualityCheck.find_quality_assessments_by_run_workflow_id_path')
@patch('app.routes.qualityCheck.get_db')
@patch('app.routes.qualityCheck.QualityAssessment')
def test_quality_check_update(mock_quality_assessment, mock_get_db, mock_find_quality_assessments, mock_update_quality_assessment, mock_insert_quality_review, client):
    mock_find_quality_assessments.return_value = [{}]
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    response = client.post('/api/qualityCheck', json={
        "run_workflow_id": "mocked_id",
        "path": "/path/to/image",
        "quality_assessment": "good"
    })

    assert response.status_code == 200
    assert response.json == {"message": "Quality assessment for image saved"}
    mock_update_quality_assessment.assert_called_once()
    mock_insert_quality_review.assert_not_called()

@patch('app.routes.qualityCheck.get_db')
def test_quality_check_value_error(mock_get_db, client):
    mock_get_db.side_effect = ValueError("Invalid input data")

    response = client.post('/api/qualityCheck', json={
        "run_workflow_id": "mocked_id",
        "path": "/path/to/image",
        "quality_assessment": "good"
    })

    assert response.status_code == 400
    assert response.json == {"error": "Invalid input data"}

@patch('app.routes.qualityCheck.get_db')
def test_quality_check_exception(mock_get_db, client):
    mock_get_db.side_effect = Exception("Database connection failed")

    response = client.post('/api/qualityCheck', json={
        "run_workflow_id": "mocked_id",
        "path": "/path/to/image",
        "quality_assessment": "good"
    })

    assert response.status_code == 500
    assert response.json == {"error": "Database connection failed"}
