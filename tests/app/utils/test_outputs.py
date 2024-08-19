import pytest
from unittest.mock import patch
from app.utils.outputs import Outputs

@pytest.fixture
def setup_mocks():
    with patch('os.path.exists') as mock_path_exists, \
         patch('app.utils.outputs.get_db') as mock_get_db, \
         patch('app.utils.outputs.find_run_workflow') as mock_find_run_workflow:
        
        mock_find_run_workflow.return_value = {'_id': 'valid_workflow_id'}
        mock_path_exists.return_value = True
        
        yield mock_find_run_workflow, mock_path_exists, mock_get_db

def test_valid_run_workflow_id(setup_mocks):
    mock_find_run_workflow, mock_path_exists, mock_get_db = setup_mocks

    outputs = Outputs(run_workflow_id='valid_workflow_id', paths=['/valid/path'])

    assert outputs.run_workflow_id == 'valid_workflow_id'

def test_invalid_run_workflow_id(setup_mocks):
    mock_find_run_workflow, mock_path_exists, mock_get_db = setup_mocks
    mock_find_run_workflow.return_value = None

    with pytest.raises(ValueError):
        Outputs(run_workflow_id='invalid_workflow_id', paths=['/valid/path'])

def test_valid_paths(setup_mocks):
    mock_find_run_workflow, mock_path_exists, mock_get_db = setup_mocks

    outputs = Outputs(run_workflow_id='valid_workflow_id', paths=['/valid/path1', '/valid/path2'])

    assert outputs.paths == ['/valid/path1', '/valid/path2']

def test_invalid_paths(setup_mocks):
    mock_find_run_workflow, mock_path_exists, mock_get_db = setup_mocks
    mock_path_exists.return_value = False

    with pytest.raises(ValueError):
        Outputs(run_workflow_id='valid_workflow_id', paths=['/invalid/path'])
