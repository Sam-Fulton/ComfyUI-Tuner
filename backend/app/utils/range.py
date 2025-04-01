from app.utils.utils import to_num
from app.utils.label_prepare_workflow import extract_base_workflow

def update_range_from_good_bad(inputs, input_key, base_lower, base_upper, good_nums, bad_nums):
    good_mean = sum(good_nums) / len(good_nums)
    bad_mean = sum(bad_nums) / len(bad_nums)
    if good_mean < bad_mean:
        new_upper = (good_mean + bad_mean) / 2
        if input_key in ('batch_size', 'steps'):
            base_lower = int(round(base_lower))
            new_upper = int(round(new_upper))
        inputs[input_key] = {"type": "range", "values": [base_lower, new_upper]}
        return f"favor lower range: {[base_lower, new_upper]}"
    else:
        new_lower = (good_mean + bad_mean) / 2
        if input_key in ('batch_size', 'steps'):
            new_lower = int(round(new_lower))
            base_upper = int(round(base_upper))
        inputs[input_key] = {"type": "range", "values": [new_lower, base_upper]}
        return f"favor upper range: {[new_lower, base_upper]}"


def update_range_fallback(inputs, input_key, good_set, bad_set):
    combined_set = good_set.union(bad_set)
    combined_nums = [to_num(v) for v in combined_set if to_num(v) is not None]
    if len(set(combined_nums)) < 2 and inputs[input_key]['type'] == 'range':
        extend_numeric_range(inputs, input_key, combined_set)
        return f"extended range: {inputs[input_key]}"
    else:
        converted_values = []
        for v in combined_set:
            num = to_num(v)
            converted_values.append(num if num is not None else v)
        determine_input_type_and_update(inputs, input_key, converted_values)
        return f"updated via determine_input_type_and_update: {inputs[input_key]}"
    
def extract_numeric_values(input_values):
    numeric_values = []
    for v in input_values:
        if isinstance(v, (int, float)):
            numeric_values.append(float(v))
        else:
            try:
                numeric_values.append(float(v))
            except (ValueError, AttributeError):
                continue
    return numeric_values

def calculate_extended_range(current_range, tuned_value, MIN_ALLOWED=1):
    try:
        current_lower = float(current_range[0])
        current_upper = float(current_range[1])
    except (ValueError, IndexError):
        return None, None

    d_low = tuned_value - current_lower
    d_high = current_upper - tuned_value

    if current_lower <= MIN_ALLOWED:
        new_lower = current_lower
        new_upper = current_upper + d_low
    else:
        if d_low < d_high:
            new_lower = current_lower - d_low
            new_upper = current_upper
        else:
            new_lower = current_lower
            new_upper = current_upper + d_high

    return new_lower, new_upper

def extend_numeric_range(inputs, input_key, input_values, MIN_ALLOWED=1):
    numeric_values = extract_numeric_values(input_values)
    if not numeric_values:
        return

    tuned_value = numeric_values[0]
    current_range = inputs[input_key]["values"]
    new_lower, new_upper = calculate_extended_range(current_range, tuned_value, MIN_ALLOWED)
    if new_lower is None or new_upper is None:
        return

    if input_key in ('batch_size', 'steps'):
        new_lower = int(round(new_lower))
        new_upper = int(round(new_upper))

    inputs[input_key] = {"type": "range", "values": [new_lower, new_upper]}


def determine_input_type_and_update(inputs, input_key, converted_values):
    if all(isinstance(v, int) for v in converted_values):
        inputs[input_key] = {"type": "range", "values": [min(converted_values), max(converted_values)]}
    elif all(isinstance(v, float) for v in converted_values):
        inputs[input_key] = {"type": "range", "values": [min(converted_values), max(converted_values)]}
    elif all(isinstance(v, str) for v in converted_values):
        inputs[input_key] = {"type": "discrete", "values": list(set(converted_values))}

def extend_range(values, min_allowed=0):
    try:
        lower = max(min_allowed, float(values[0]))
        upper = float(values[1])
    except (ValueError, TypeError):
        return None

    diff = upper - lower
    return [max(min_allowed, lower - diff), upper + diff]

def extend_ranges_from_base(base_workflow):
    workflow_data = extract_base_workflow(base_workflow)
    for node_data in workflow_data.values():
        inputs = node_data.get('inputs', {})
        for input_key, input_val in inputs.items():
            if isinstance(input_val, dict) and input_val.get('type') == 'range':
                values = input_val.get('values', [])
                if isinstance(values, list) and len(values) == 2:
                    extended = extend_range(values, min_allowed=0)
                    if extended is not None:
                        inputs[input_key] = {"type": "range", "values": extended}
    
    print(base_workflow, flush=True)
    return workflow_data