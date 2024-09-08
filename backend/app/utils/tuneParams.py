import random
import copy
from app.utils.mongo import find_quality_assessments_by_run_workflow_id, find_run_workflow
from app.utils.qualityAssessment import QualityAssessment

def label_workflow_for_random_sampling(base_workflow):
    for k in base_workflow.keys():
        inputs = base_workflow[k]['inputs']
        for input_key, input_value in inputs.items():
            if (isinstance(input_value, dict) 
                and 'type' in input_value 
                and 'values' in input_value 
                and len(input_value) == 2 
                and input_value['type'] in ['discrete', 'range']):
                continue
            
            if isinstance(input_value, list):
                if len(set(map(type, input_value))) == 1:
                    if all(isinstance(v, str) for v in input_value):
                        base_workflow[k]['inputs'][input_key] = {"type": "discrete", "values": input_value}
                    elif all(isinstance(v, int) for v in input_value):
                        if len(input_value) > 2:
                            base_workflow[k]['inputs'][input_key] = {"type": "discrete", "values": input_value}
                        else:
                            base_workflow[k]['inputs'][input_key] = {"type": "range", "values": input_value}
                    elif all(isinstance(v, float) for v in input_value):
                        if len(input_value) > 2:
                            base_workflow[k]['inputs'][input_key] = {"type": "discrete", "values": input_value}
                        else:
                            base_workflow[k]['inputs'][input_key] = {"type": "range", "values": input_value}
        
    return base_workflow


def prepare_run_workflow(base_workflow): 
    run_workflow = copy.deepcopy(base_workflow)
    for k in run_workflow.keys():
        inputs = run_workflow[k]['inputs']
        for input_key, input_value in inputs.items():
            if isinstance(input_value, dict) and "type" in input_value and "values" in input_value:
                if input_value["type"] == "discrete":
                    run_workflow[k]['inputs'][input_key] = random.choice(input_value["values"])
                elif input_value["type"] == "range":
                    if all(isinstance(v, int) for v in input_value["values"]):
                        run_workflow[k]['inputs'][input_key] = random.randint(input_value["values"][0], input_value["values"][1])
                    elif all(isinstance(v, float) for v in input_value["values"]):
                        run_workflow[k]['inputs'][input_key] = random.uniform(input_value["values"][0], input_value["values"][1])
    
    return run_workflow

def filter_good_workflows(run_workflow_ids, threshold, db):
    good_workflows = []

    for run_workflow_id in run_workflow_ids:
        run_workflow = find_run_workflow(db, run_workflow_id)
        quality_assessments = find_quality_assessments_by_run_workflow_id(db, run_workflow_id)

        if run_workflow and quality_assessments:
            good_count = sum(1 for qa in quality_assessments if QualityAssessment(qa['run_workflow_id'], qa['path'], qa['quality_assessment'])._quality_assessment == 'good')
            total_assessments = len(quality_assessments)
            
            if total_assessments > 0 and good_count / total_assessments >= threshold:
                good_workflows.append(run_workflow)
    
    return good_workflows

def combine_differing_inputs(good_workflows):
    combined_assessments = {}

    for workflow in good_workflows:
        for node_key, node_data in workflow.items():
            if 'inputs' in node_data:
                inputs = node_data['inputs']
                for input_key, input_value in inputs.items():
                    if node_key not in combined_assessments:
                        combined_assessments[node_key] = {}
                    if input_key not in combined_assessments[node_key]:
                        combined_assessments[node_key][input_key] = set()
                    combined_assessments[node_key][input_key].add(str(input_value))

    for node_key, inputs in list(combined_assessments.items()):
        for input_key, values in list(inputs.items()):
            if len(values) <= 1:
                del combined_assessments[node_key][input_key]
        if not combined_assessments[node_key]:
            del combined_assessments[node_key]
    
    return combined_assessments

def convert_and_adjust_values(base_workflow, combined_assessments):
    if 'value' in base_workflow.keys():
        base_workflow_value = base_workflow['value']
    else:
        base_workflow_value = base_workflow

    for node_key in base_workflow_value.keys():
        inputs = base_workflow_value[node_key]['inputs']
        for input_key in inputs.keys():
            if input_key in combined_assessments.get(node_key, {}):
                input_values = combined_assessments[node_key][input_key]
                
                converted_values = []
                for v in input_values:
                    try:
                        if '.' in v:
                            converted_values.append(float(v))
                        else:
                            converted_values.append(int(v))
                    except ValueError:
                        converted_values.append(v)

                if len(converted_values) == 0 or len(set(converted_values)) < 2:
                    extend_numeric_range(inputs, input_key, input_values)
                else:
                    determine_input_type_and_update(inputs, input_key, converted_values)
    
    return base_workflow

def extend_numeric_range(inputs, input_key, input_values):
    numeric_values = [float(v) for v in input_values if isinstance(v, (int, float)) or v.replace('.', '', 1).isdigit()]
    
    if numeric_values:
        min_val, max_val = min(numeric_values), max(numeric_values)
        range_diff = max_val - min_val
        extended_min = min_val - range_diff
        extended_max = max_val + range_diff
        inputs[input_key] = {"type": "range", "values": [extended_min, extended_max]}

def determine_input_type_and_update(inputs, input_key, converted_values):
    if all(isinstance(v, int) for v in converted_values):
        inputs[input_key] = {"type": "range", "values": [min(converted_values), max(converted_values)]}
    elif all(isinstance(v, float) for v in converted_values):
        inputs[input_key] = {"type": "range", "values": [min(converted_values), max(converted_values)]}
    elif all(isinstance(v, str) for v in converted_values):
        inputs[input_key] = {"type": "discrete", "values": list(set(converted_values))}

def update_ranges_by_quality_control(run_workflow_ids, base_workflow, threshold, db):
    good_workflows = filter_good_workflows(run_workflow_ids, threshold, db)
    combined_assessments = combine_differing_inputs(good_workflows)
    updated_base_workflow = convert_and_adjust_values(base_workflow, combined_assessments)

    return updated_base_workflow
