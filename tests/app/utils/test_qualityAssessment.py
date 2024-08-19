import pytest
from unittest.mock import patch
from app.utils.qualityAssessment import QualityAssessment

@pytest.fixture
def setup_mocks():
    with patch('os.path.exists') as mock_path_exists, \
         patch('app.utils.qualityAssessment.get_db') as mock_get_db, \
         patch('app.utils.qualityAssessment.find_run_workflow') as mock_find_run_workflow:
        
        mock_find_run_workflow.return_value = {'_id': 'valid_workflow_id'}
        mock_path_exists.return_value = True
        
        yield mock_find_run_workflow, mock_path_exists, mock_get_db

def test_valid_run_workflow_id(setup_mocks):
    mock_find_run_workflow, mock_path_exists, mock_get_db = setup_mocks

    qa = QualityAssessment(run_workflow_id='valid_workflow_id', path='/valid/path', quality_assessment='good')
    assert qa.run_workflow_id == 'valid_workflow_id'

def test_invalid_run_workflow_id(setup_mocks):
    mock_find_run_workflow, mock_path_exists, mock_get_db = setup_mocks
    mock_find_run_workflow.return_value = None

    with pytest.raises(ValueError):
        QualityAssessment(run_workflow_id='invalid_workflow_id', path='/valid/path', quality_assessment='good')

def test_valid_path(setup_mocks):
    mock_find_run_workflow, mock_path_exists, mock_get_db = setup_mocks

    qa = QualityAssessment(run_workflow_id='valid_workflow_id', path='/valid/path', quality_assessment='good')
    assert qa.path == '/valid/path'

def test_invalid_path(setup_mocks):
    mock_find_run_workflow, mock_path_exists, mock_get_db = setup_mocks
    mock_path_exists.return_value = False

    with pytest.raises(ValueError):
        QualityAssessment(run_workflow_id='valid_workflow_id', path='/invalid/path', quality_assessment='good')

def test_valid_quality_assessment(setup_mocks):
    mock_find_run_workflow, mock_path_exists, mock_get_db = setup_mocks

    qa = QualityAssessment(run_workflow_id='valid_workflow_id', path='/valid/path', quality_assessment='good')
    assert qa.quality_assessment == 'good'

    qa = QualityAssessment(run_workflow_id='valid_workflow_id', path='/valid/path', quality_assessment='bad')
    assert qa.quality_assessment == 'bad'

def test_invalid_quality_assessment(setup_mocks):
    mock_find_run_workflow, mock_path_exists, mock_get_db = setup_mocks

    with pytest.raises(ValueError):
        QualityAssessment(run_workflow_id='valid_workflow_id', path='/valid/path', quality_assessment='excellent')
