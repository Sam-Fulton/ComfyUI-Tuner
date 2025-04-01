import copy
import random

def is_already_labeled(input_value):
    return (isinstance(input_value, dict) and
            'type' in input_value and
            'values' in input_value and
            len(input_value) == 2 and
            input_value['type'] in ['discrete', 'range'])


def label_input_list(input_list):
    if not input_list:
        return input_list

    common_type = type(input_list[0])
    if not all(isinstance(v, common_type) for v in input_list):
        return input_list

    if common_type is str:
        return {"type": "discrete", "values": input_list}
    elif common_type in (int, float):
        label_type = "discrete" if len(input_list) > 2 else "range"
        return {"type": label_type, "values": input_list}
    
    return input_list


def label_workflow_for_random_sampling(base_workflow):
    for node_key, node_data in base_workflow.items():
        inputs = node_data.get('inputs', {})
        for input_key, input_value in inputs.items():
            if is_already_labeled(input_value):
                continue
            if isinstance(input_value, list):
                base_workflow[node_key]['inputs'][input_key] = label_input_list(input_value)
    return base_workflow


def sample_range(values):
    if all(isinstance(v, int) for v in values):
        return random.randint(values[0], values[1])
    elif all(isinstance(v, float) for v in values):
        return random.uniform(values[0], values[1])
    else:
        raise ValueError("Range values must be all int or all float.")

def prepare_run_workflow(base_workflow):
    base_workflow_value = extract_base_workflow(base_workflow)
    run_workflow = copy.deepcopy(base_workflow_value)

    for node_key, node_data in run_workflow.items():
        print(f"node key {node_key}", flush=True)
        inputs = node_data.get('inputs', {})
        for input_key, input_value in inputs.items():
            if isinstance(input_value, dict) and "type" in input_value and "values" in input_value:
                print(f"\n{input_value}", flush=True)
                if input_value["type"] == "discrete":
                    run_workflow[node_key]['inputs'][input_key] = random.choice(input_value["values"])
                elif input_value["type"] == "range":
                    run_workflow[node_key]['inputs'][input_key] = sample_range(input_value["values"])
    return run_workflow


def extract_base_workflow(base_workflow):
    base_workflow_value = base_workflow.get('value', base_workflow)

    return base_workflow_value
