from unittest.mock import patch, MagicMock
from app.utils.range import (
    extend_numeric_range, 
    determine_input_type_and_update, 
    update_range_from_good_bad, 
    extract_numeric_values,
    calculate_extended_range,
    extend_range,
    extend_ranges_from_base,
    update_range_fallback
)


def test_update_range_from_good_bad_lower():
    inputs = {}
    input_key = "quality"
    base_lower = 0.0
    base_upper = 10.0
    good_nums = [1.0, 2.0]
    bad_nums = [8.0, 9.0]

    expected_message = "favor lower range: [0.0, 5.0]"
    message = update_range_from_good_bad(inputs, input_key, base_lower, base_upper, good_nums, bad_nums)
    
    assert message == expected_message
    assert inputs[input_key] == {"type": "range", "values": [0.0, 5.0]}

def test_update_range_from_good_bad_upper():
    inputs = {}
    input_key = "quality"
    base_lower = 0.0
    base_upper = 10.0
    good_nums = [8.0, 9.0]
    bad_nums = [1.0, 2.0]

    expected_message = "favor upper range: [5.0, 10.0]"
    message = update_range_from_good_bad(inputs, input_key, base_lower, base_upper, good_nums, bad_nums)
    
    assert message == expected_message
    assert inputs[input_key] == {"type": "range", "values": [5.0, 10.0]}

def test_update_range_from_good_bad_with_steps_lower():
    inputs = {}
    input_key = "steps"
    base_lower = 5.0
    base_upper = 15.0
    good_nums = [10, 11]
    bad_nums = [13, 14]

    expected_message = "favor lower range: [5, 12]"
    message = update_range_from_good_bad(inputs, input_key, base_lower, base_upper, good_nums, bad_nums)
    
    assert message == expected_message
    assert inputs[input_key] == {"type": "range", "values": [5, 12]}

def test_update_range_from_good_bad_with_steps_upper():
    inputs = {}
    input_key = "steps"
    base_lower = 5.0
    base_upper = 15.0
    good_nums = [13, 14]
    bad_nums = [10, 11]

    expected_message = "favor upper range: [12, 15]"
    message = update_range_from_good_bad(inputs, input_key, base_lower, base_upper, good_nums, bad_nums)
    
    assert message == expected_message
    assert inputs[input_key] == {"type": "range", "values": [12, 15]}


def test_update_range_fallback_extended_branch():
    inputs = {"param": {"type": "range", "values": [0, 10]}}
    good_set = {"5"}
    bad_set = set()

    with patch("app.utils.range.extend_numeric_range") as mock_extend, \
         patch("app.utils.range.determine_input_type_and_update") as mock_determine:
        result = update_range_fallback(inputs, "param", good_set, bad_set)
        
        mock_extend.assert_called_once_with(inputs, "param", good_set.union(bad_set))
        mock_determine.assert_not_called()
        assert result.startswith("extended range:")

def test_update_range_fallback_update_branch():
    inputs = {"param": {"type": "range", "values": [0, 10]}}
    good_set = {"5", "7"}
    bad_set = set()

    with patch("app.utils.range.extend_numeric_range") as mock_extend, \
         patch("app.utils.range.determine_input_type_and_update") as mock_determine:
        result = update_range_fallback(inputs, "param", good_set, bad_set)
        
        mock_extend.assert_not_called()
        mock_determine.assert_called_once()
        assert result.startswith("updated via determine_input_type_and_update:")

def test_extract_numeric_values_with_numbers():
    values = [1, 2.5, 3]
    expected = [1.0, 2.5, 3.0]
    assert extract_numeric_values(values) == expected

def test_extract_numeric_values_with_numeric_strings():
    values = ["1", "2.5", "3"]
    expected = [1.0, 2.5, 3.0]
    assert extract_numeric_values(values) == expected

def test_extract_numeric_values_with_mixed_types():
    values = [1, "2.5", "abc", 4.0, "5xyz", "6"]
    expected = [1.0, 2.5, 4.0, 6.0]
    assert extract_numeric_values(values) == expected

def test_extract_numeric_values_empty_list():
    values = []
    expected = []
    assert extract_numeric_values(values) == expected



def test_calculate_extended_range_lower_branch():
    current_range = [0, 10]
    tuned_value = 2
    new_lower, new_upper = calculate_extended_range(current_range, tuned_value)
    assert new_lower == 0
    assert new_upper == 12

def test_calculate_extended_range_lower_branch_exact_min_allowed():
    current_range = [1, 5]
    tuned_value = 3
    new_lower, new_upper = calculate_extended_range(current_range, tuned_value)
    assert new_lower == 1
    assert new_upper == 7

def test_calculate_extended_range_higher_branch_favor_lower():
    current_range = [2, 10]
    tuned_value = 3
    new_lower, new_upper = calculate_extended_range(current_range, tuned_value)
    assert new_lower == 1
    assert new_upper == 10

def test_calculate_extended_range_higher_branch_favor_upper():
    current_range = [2, 10]
    tuned_value = 8
    new_lower, new_upper = calculate_extended_range(current_range, tuned_value)
    assert new_lower == 2
    assert new_upper == 12

def test_calculate_extended_range_invalid_input():
    current_range = []
    tuned_value = 5
    new_lower, new_upper = calculate_extended_range(current_range, tuned_value)
    assert new_lower is None and new_upper is None

    current_range = ["a", "b"]
    new_lower, new_upper = calculate_extended_range(current_range, tuned_value)
    assert new_lower is None and new_upper is None


def test_extend_range_valid_default_min_allowed():
    result = extend_range([5, 10])
    assert result == [0, 15]

def test_extend_range_valid_custom_min_allowed():
    result = extend_range([2, 6], min_allowed=3)
    assert result == [3, 9]

def test_extend_range_with_negative_lower():
    result = extend_range([-2, 4])
    assert result == [0, 8]

def test_extend_range_invalid_value():
    result = extend_range(["a", 10])
    assert result is None

def test_extend_range_non_iterable():
    result = extend_range(None)
    assert result is None


def test_extend_numeric_range_normal():
    inputs = {"param": {"type": "range", "values": [0, 10]}}
    input_values = [2]

    extend_numeric_range(inputs, "param", input_values, MIN_ALLOWED=1)
    assert inputs["param"] == {"type": "range", "values": [0, 12]}

def test_extend_numeric_range_rounding():
    inputs = {"steps": {"type": "range", "values": [5.5, 10.2]}}
    input_values = [3.7]
    extend_numeric_range(inputs, "steps", input_values, MIN_ALLOWED=1)
    assert inputs["steps"] == {"type": "range", "values": [7, 10]}

def test_extend_numeric_range_no_numeric_values():
    original_range = [2, 4]
    inputs = {"param": {"type": "range", "values": original_range.copy()}}
    input_values = ["non-numeric", "also non-numeric"]
    extend_numeric_range(inputs, "param", input_values, MIN_ALLOWED=1)
    assert inputs["param"] == {"type": "range", "values": original_range}

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



def dummy_extract_base_workflow(base_workflow):
    return {
        "node1": {
            "inputs": {
                "param1": {"type": "range", "values": [5, 10]},
                "param2": {"type": "other", "values": "unchanged"}
            }
        },
        "node2": {
            "inputs": {
                "paramA": {"type": "range", "values": [0, 3]}
            }
        }
    }

@patch("app.utils.range.extract_base_workflow", side_effect=dummy_extract_base_workflow)
def test_extend_ranges_from_base(mock_extract):
    base_workflow = MagicMock()
    workflow_data = extend_ranges_from_base(base_workflow)
    
    print(workflow_data)
    expected_workflow_data = {
        "node1": {
            "inputs": {
                "param1": {"type": "range", "values": [0, 15]},
                "param2": {"type": "other", "values": "unchanged"}
            }
        },
        "node2": {
            "inputs": {
                "paramA": {"type": "range", "values": [0, 6]}
            }
        }
    }
    
    assert workflow_data == expected_workflow_data