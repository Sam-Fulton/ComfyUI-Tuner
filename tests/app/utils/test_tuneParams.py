import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from app.utils.tuneParams import (
    label_workflow_for_random_sampling,
    prepare_run_workflow,
    filter_good_workflows,
    combine_differing_inputs,
    convert_and_adjust_values,
    update_ranges_by_quality_control,
    extend_numeric_range,
    determine_input_type_and_update,
)

@pytest.fixture
def sample_workflow():
    return {
        "1": {
            "class_type": "SaveImage",
            "inputs": {
                "filename": ["image_1.png", "image_2.png"],
                "quality": [1, 2, 3],
                "scale": [0.1, 0.2]
            }
        },
        "2": {
            "class_type": "SaveVideo",
            "inputs": {
                "filename": ["video_1.mp4", "video_2.mp4"],
                "resolution": [720, 1080],
                "quality": [0.8, 1.0]
            }
        }
    }

def mock_quality_assessment_constructor(run_workflow_id, path, quality_assessment):
    return MagicMock(_quality_assessment=quality_assessment)

def test_label_workflow_for_random_sampling(sample_workflow):
    labeled_workflow = label_workflow_for_random_sampling(sample_workflow)
    assert labeled_workflow["1"]["inputs"]["filename"] == {"type": "discrete", "values": ["image_1.png", "image_2.png"]}
    assert labeled_workflow["1"]["inputs"]["quality"] == {"type": "discrete", "values": [1, 2, 3]}
    assert labeled_workflow["1"]["inputs"]["scale"] == {"type": "range", "values": [0.1, 0.2]}
    assert labeled_workflow["2"]["inputs"]["filename"] == {"type": "discrete", "values": ["video_1.mp4", "video_2.mp4"]}
    assert labeled_workflow["2"]["inputs"]["resolution"] == {"type": "range", "values": [720, 1080]}
    assert labeled_workflow["2"]["inputs"]["quality"] == {"type": "range", "values": [0.8, 1.0]}

@patch('random.choice', side_effect=lambda x: x[0])
@patch('random.randint', side_effect=lambda x, y: x)
@patch('random.uniform', side_effect=lambda x, y: x)
def test_prepare_run_workflow(mock_choice, mock_randint, mock_uniform, sample_workflow):
    labeled_workflow = label_workflow_for_random_sampling(sample_workflow)
    run_workflow = prepare_run_workflow(labeled_workflow)
    assert run_workflow["1"]["inputs"]["filename"] == "image_1.png"
    assert run_workflow["1"]["inputs"]["quality"] == 1
    assert run_workflow["1"]["inputs"]["scale"] == 0.1
    assert run_workflow["2"]["inputs"]["filename"] == "video_1.mp4"
    assert run_workflow["2"]["inputs"]["resolution"] == 720
    assert run_workflow["2"]["inputs"]["quality"] == 0.8

@patch('app.utils.tuneParams.QualityAssessment')
@patch('app.utils.tuneParams.find_quality_assessments_by_run_workflow_id')
@patch('app.utils.tuneParams.find_run_workflow')
def test_filter_good_workflows(mock_find_workflow, mock_find_assessments, mock_quality_assessment, sample_workflow):
    mock_workflow_id = str(ObjectId())

    mock_find_workflow.return_value = sample_workflow
    
    mock_find_assessments.return_value = [
        {"run_workflow_id": mock_workflow_id, "path": "/path1", "quality_assessment": "good"},
        {"run_workflow_id": mock_workflow_id, "path": "/path2", "quality_assessment": "bad"}
    ]

    mock_quality_assessment.side_effect = mock_quality_assessment_constructor

    good_workflows = filter_good_workflows([mock_workflow_id], 0.5, MagicMock())
    
    assert len(good_workflows) == 1

def test_combine_differing_inputs():
    workflows = [
        {
            "1": {"inputs": {"quality": 1, "scale": 0.1}},
            "2": {"inputs": {"resolution": 720, "quality": 0.8}}
        },
        {
            "1": {"inputs": {"quality": 2, "scale": 0.2}},
            "2": {"inputs": {"resolution": 1080, "quality": 1.0}}
        }
    ]
    combined_inputs = combine_differing_inputs(workflows)
    assert combined_inputs["1"]["quality"] == {"1", "2"}
    assert combined_inputs["1"]["scale"] == {"0.1", "0.2"}
    assert combined_inputs["2"]["resolution"] == {"720", "1080"}
    assert combined_inputs["2"]["quality"] == {"0.8", "1.0"}

@patch('app.utils.tuneParams.extend_numeric_range')
def test_convert_and_adjust_values(mock_extend_numeric_range, sample_workflow):
    combined_assessments = {
        "1": {"quality": {"1", "2"}, "scale": {"0.1", "0.2"}},
        "2": {"resolution": {"720", "1080"}, "quality": {"0.8", "1.0"}}
    }
    updated_workflow = convert_and_adjust_values(sample_workflow, combined_assessments)
    assert updated_workflow["1"]["inputs"]["quality"] == {"type": "range", "values": [1, 2]}
    assert updated_workflow["1"]["inputs"]["scale"] == {"type": "range", "values": [0.1, 0.2]}
    assert updated_workflow["2"]["inputs"]["resolution"] == {"type": "range", "values": [720, 1080]}
    assert updated_workflow["2"]["inputs"]["quality"] == {"type": "range", "values": [0.8, 1.0]}
    mock_extend_numeric_range.assert_not_called()

@patch('app.utils.tuneParams.filter_good_workflows')
@patch('app.utils.tuneParams.convert_and_adjust_values')
def test_update_ranges_by_quality_control(mock_convert, mock_filter, sample_workflow):
    mock_filter.return_value = [sample_workflow]
    mock_convert.return_value = sample_workflow
    updated_workflow = update_ranges_by_quality_control(["1"], sample_workflow, 0.5, MagicMock())
    assert updated_workflow == sample_workflow
    mock_filter.assert_called_once()
    mock_convert.assert_called_once()

def test_extend_numeric_range():
    inputs = {"input_key": {"type": "range", "values": [5, 10]}}
    input_values = {"5", "10"}
    extend_numeric_range(inputs, "input_key", input_values)
    assert inputs["input_key"]["type"] == "range"
    assert inputs["input_key"]["values"] == [0, 15]

    inputs = {"input_key": {"type": "range", "values": [7, 7]}}
    input_values = {"7"}
    extend_numeric_range(inputs, "input_key", input_values)
    assert inputs["input_key"]["values"] == [7, 7]

def test_determine_input_type_and_update():
    inputs = {"input_key": {}}
    converted_values = [1, 2, 3]
    determine_input_type_and_update(inputs, "input_key", converted_values)
    assert inputs["input_key"]["type"] == "range"
    assert inputs["input_key"]["values"] == [1, 3]

    inputs = {"input_key": {}}
    converted_values = [0.1, 0.2, 0.3]
    determine_input_type_and_update(inputs, "input_key", converted_values)
    assert inputs["input_key"]["type"] == "range"
    assert inputs["input_key"]["values"] == [0.1, 0.3]

    inputs = {"input_key": {}}
    converted_values = ["a", "b", "c"]
    determine_input_type_and_update(inputs, "input_key", converted_values)
    assert inputs["input_key"]["type"] == "discrete"
    assert set(inputs["input_key"]["values"]) == {"a", "b", "c"}

    inputs = {"input_key": {}}
    converted_values = [1, "a", 0.1]
    determine_input_type_and_update(inputs, "input_key", converted_values)
    assert inputs == {"input_key": {}}
