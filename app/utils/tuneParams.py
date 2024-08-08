import random
from utils.mongo import find_quality_assessments_by_run_workflow_id, find_run_workflow
from utils.qualityAssessment import QualityAssessment

def label_workflow_for_random_sampling(base_workflow):
    for k in base_workflow.keys():
        inputs = base_workflow[k]['inputs']
        for input_key, input_value in inputs.items():
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
    print(base_workflow, flush=True)
    for k in base_workflow.keys():
        inputs = base_workflow[k]['inputs']
        for input_key, input_value in inputs.items():
            if isinstance(input_value, dict) and "type" in input_value and "values" in input_value:
                if input_value["type"] == "discrete":
                    base_workflow[k]['inputs'][input_key] = random.choice(input_value["values"])
                elif input_value["type"] == "range":
                    if all(isinstance(v, int) for v in input_value["values"]):
                        base_workflow[k]['inputs'][input_key] = random.randint(input_value["values"][0], input_value["values"][1])
                    elif all(isinstance(v, float) for v in input_value["values"]):
                        base_workflow[k]['inputs'][input_key] = random.uniform(input_value["values"][0], input_value["values"][1])
    
    return base_workflow

def update_ranges_by_quality_control(run_workflow_ids, base_workflow, threshold, db):
    combined_good_assessments = {}

    for run_workflow_id in run_workflow_ids:
        run_workflow = find_run_workflow(db, run_workflow_id)
        quality_assessments = find_quality_assessments_by_run_workflow_id(db, run_workflow_id)
        if run_workflow and quality_assessments:
            good_count = 0
            bad_count = 0
            for qa in quality_assessments:
                quality_assessment = QualityAssessment(qa['run_workflow_id'], qa['path'], qa['quality_assessment'])
                if quality_assessment.quality_assessment == 'good':
                    good_count += 1
                else:
                    bad_count += 1
            
            total_assessments = good_count + bad_count
            if total_assessments > 0 and good_count / total_assessments >= threshold:
                for key, value in run_workflow['inputs'].items():
                    if key not in combined_good_assessments:
                        combined_good_assessments[key] = []
                    combined_good_assessments[key].append(value)

    for k in base_workflow.keys():
        inputs = base_workflow[k]['inputs']
        for input_key in inputs.keys():
            if input_key in combined_good_assessments:
                input_values = combined_good_assessments[input_key]
                if all(isinstance(v, int) for v in input_values):
                    inputs[input_key] = {"type": "range", "values": [min(input_values), max(input_values)]}
                elif all(isinstance(v, float) for v in input_values):
                    inputs[input_key] = {"type": "range", "values": [min(input_values), max(input_values)]}
                elif all(isinstance(v, str) for v in input_values):
                    inputs[input_key] = {"type": "discrete", "values": list(set(input_values))}

    return base_workflow