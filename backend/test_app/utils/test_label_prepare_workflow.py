import pytest
from unittest.mock import patch

from app.utils.label_prepare_workflow import (
    label_workflow_for_random_sampling, 
    prepare_run_workflow,
    is_already_labeled,
    label_input_list,
    sample_range
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


def test_is_already_labeled_true_discrete():
    labeled = {"type": "discrete", "values": [1, 2, 3]}
    assert is_already_labeled(labeled) is True

def test_is_already_labeled_true_range():
    labeled = {"type": "range", "values": [0, 10]}
    assert is_already_labeled(labeled) is True

def test_is_already_labeled_invalid_type():
    not_labeled = {"type": "other", "values": [0, 10]}
    assert is_already_labeled(not_labeled) is False

def test_is_already_labeled_extra_keys():
    not_labeled = {"type": "range", "values": [0, 10], "extra": "value"}
    assert is_already_labeled(not_labeled) is False

def test_is_already_labeled_non_dict():
    not_labeled = [1, 2, 3]
    assert is_already_labeled(not_labeled) is False

def test_is_already_labeled_none():
    not_labeled = None
    assert is_already_labeled(not_labeled) is False

def test_label_input_list_empty():
    assert label_input_list([]) == []

def test_label_input_list_inconsistent_types():
    input_list = [1, "2", 3]
    assert label_input_list(input_list) == input_list

def test_label_input_list_strings():
    input_list = ["a", "b", "c"]
    expected = {"type": "discrete", "values": ["a", "b", "c"]}
    assert label_input_list(input_list) == expected

def test_label_input_list_ints_more_than_two():
    input_list = [1, 2, 3]
    expected = {"type": "discrete", "values": [1, 2, 3]}
    assert label_input_list(input_list) == expected

def test_label_input_list_ints_two_elements():
    input_list = [4, 5]
    expected = {"type": "range", "values": [4, 5]}
    assert label_input_list(input_list) == expected

def test_label_input_list_floats_more_than_two():
    input_list = [1.1, 2.2, 3.3]
    expected = {"type": "discrete", "values": [1.1, 2.2, 3.3]}
    assert label_input_list(input_list) == expected

def test_label_input_list_floats_two_elements():
    input_list = [7.7, 8.8]
    expected = {"type": "range", "values": [7.7, 8.8]}
    assert label_input_list(input_list) == expected

def test_label_input_list_other_types():
    input_list = [{"a": 1}, {"a": 2}]
    assert label_input_list(input_list) == input_list

@patch('random.randint', side_effect=lambda a, b: a)
def test_sample_range_int(mock_randint):
    values = [10, 20]
    result = sample_range(values)
    assert result == 10
    mock_randint.assert_called_once_with(10, 20)

@patch('random.uniform', side_effect=lambda a, b: a)
def test_sample_range_float(mock_uniform):
    values = [1.1, 2.2]
    result = sample_range(values)
    assert result == 1.1
    mock_uniform.assert_called_once_with(1.1, 2.2)

def test_sample_range_mixed_types():
    values = [1, 2.2]
    with pytest.raises(ValueError) as excinfo:
        sample_range(values)
    assert "Range values must be all int or all float." in str(excinfo.value)

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