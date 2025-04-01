import pytest
from unittest.mock import patch, MagicMock
from app.utils.tuneParams import (
    combine_differing_inputs,
    convert_and_adjust_values,
    update_ranges_by_quality_control,
    sort_workflows
)


@pytest.fixture
def sample_base_workflow():
    return {
        "1": {
            "inputs": {
                "quality": {"type": "range", "values": [0, 10]},
                "scale": {"type": "range", "values": [0, 1]}
            }
        },
        "2": {
            "inputs": {
                "steps": {"type": "range", "values": [0, 30]},
                "cfg": {"type": "range", "values": [0, 10]}
            }
        }
    }

@pytest.fixture
def sample_run_workflows():
    return [
        {
            "1": {"inputs": {"quality": 5, "scale": 0.5}},
            "2": {"inputs": {"steps": 25, "cfg": 7}}
        },
        {
            "1": {"inputs": {"quality": 6, "scale": 0.6}},
            "2": {"inputs": {"steps": 20, "cfg": 6}}
        }
    ]

def mock_quality_assessment_constructor(run_workflow_id, path, quality_assessment):
    return MagicMock(_quality_assessment=quality_assessment)

@patch('app.utils.tuneParams.QualityAssessment')
@patch('app.utils.tuneParams.find_quality_assessments_by_run_workflow_id')
@patch('app.utils.tuneParams.find_run_workflow')
def test_sort_workflows(mock_find_run_workflow, mock_find_assessments, mock_quality_assessment, sample_run_workflows):
    good_id = "good_id"
    bad_id = "bad_id"
    
    def side_effect_find_run_workflow(db, run_workflow_id):
        if run_workflow_id == good_id:
            return sample_run_workflows[0]
        elif run_workflow_id == bad_id:
            return sample_run_workflows[1]
        else:
            return None
    mock_find_run_workflow.side_effect = side_effect_find_run_workflow
    
    def side_effect_find_assessments(db, run_workflow_id):
        if run_workflow_id == good_id:
            return [
                {"run_workflow_id": good_id, "path": "/path1", "quality_assessment": "good"},
                {"run_workflow_id": good_id, "path": "/path2", "quality_assessment": "good"},
            ]
        elif run_workflow_id == bad_id:
            return [
                {"run_workflow_id": bad_id, "path": "/path1", "quality_assessment": "good"},
                {"run_workflow_id": bad_id, "path": "/path2", "quality_assessment": "bad"},
            ]
        else:
            return []
    mock_find_assessments.side_effect = side_effect_find_assessments
    
    mock_quality_assessment.side_effect = lambda run_workflow_id, path, qa: MagicMock(_quality_assessment=qa)
    
    good_workflows, bad_workflows = sort_workflows([good_id, bad_id], 0.8, MagicMock())
    
    assert len(good_workflows) == 1
    assert len(bad_workflows) == 1

def test_combine_differing_inputs(sample_run_workflows, sample_base_workflow):
    combined_assessments = combine_differing_inputs(sample_run_workflows, sample_base_workflow)
    
    expected = {
        "1": {
            "quality": {"5", "6"},
            "scale": {"0.5", "0.6"}
        },
        "2": {
            "steps": {"25", "20"},
            "cfg": {"7", "6"}
        }
    }
    
    assert combined_assessments == expected

def test_convert_and_adjust_values(sample_base_workflow):
    
    good_tune_params = {
        "1": {"quality": {"1", "2"}},
        "2": {"steps": {"20", "25"}}
    }
    bad_tune_params = {
        "1": {"scale": {"0.1", "0.2"}},
        "2": {"cfg": {"6", "7"}}
    }

    updated_workflow = convert_and_adjust_values(sample_base_workflow, good_tune_params, bad_tune_params)
    
    expected = {
        "1": {
            "inputs": {
                "quality": {"type": "range", "values": [1, 2]},
                "scale": {"type": "range", "values": [0.1, 0.2]}
            }
        },
        "2": {
            "inputs": {
                "steps": {"type": "range", "values": [20, 25]},
                "cfg": {"type": "range", "values": [6, 7]}
            }
        }
    }
    
    assert updated_workflow == expected

@patch('app.utils.tuneParams.convert_and_adjust_values')
@patch('app.utils.tuneParams.sort_workflows')
def test_update_ranges_by_quality_control(mock_sort_workflows, mock_convert, sample_base_workflow):
    mock_sort_workflows.return_value = ([{"dummy": "workflow"}], [])
    mock_convert.return_value = sample_base_workflow
    updated_workflow = update_ranges_by_quality_control(["1"], sample_base_workflow, 0.5, MagicMock())
    assert updated_workflow == sample_base_workflow
    mock_sort_workflows.assert_called_once()
    mock_convert.assert_called_once()

@patch('app.utils.tuneParams.extend_ranges_from_base')
@patch('app.utils.tuneParams.sort_workflows')
def test_update_ranges_by_quality_control_no_good(mock_sort_workflows, mock_extend, sample_base_workflow):
    mock_sort_workflows.return_value = ([], [{"dummy": "workflow"}])
    mock_extend.return_value = sample_base_workflow
    updated_workflow = update_ranges_by_quality_control(["1"], sample_base_workflow, 0.5, MagicMock())
    assert updated_workflow == sample_base_workflow
    mock_sort_workflows.assert_called_once()
    mock_extend.assert_called_once()
