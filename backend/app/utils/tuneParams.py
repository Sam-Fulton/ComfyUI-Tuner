from app.utils.mongo import find_quality_assessments_by_run_workflow_id, find_run_workflow
from app.utils.qualityAssessment import QualityAssessment
from app.utils.label_prepare_workflow import extract_base_workflow
from app.utils.range import update_range_from_good_bad, update_range_fallback, extend_ranges_from_base
from app.utils.utils import to_num

def sort_workflows(run_workflow_ids, threshold, db):
    good_workflows = []
    bad_workflows = []
    for run_workflow_id in run_workflow_ids:
        run_workflow = find_run_workflow(db, run_workflow_id)
        quality_assessments = find_quality_assessments_by_run_workflow_id(db, run_workflow_id)

        if run_workflow and quality_assessments:
            good_count = sum(1 for qa in quality_assessments if QualityAssessment(qa['run_workflow_id'], qa['path'], qa['quality_assessment'])._quality_assessment == 'good')
            total_assessments = len(quality_assessments)
            
            if total_assessments > 0 and good_count / total_assessments >= threshold:
                good_workflows.append(run_workflow)
            else:
                bad_workflows.append(run_workflow)

    return good_workflows, bad_workflows

def extract_tuned_input_keys(base_workflow):
    tuned_keys = {}
    base_workflow_value = extract_base_workflow(base_workflow)
    for node_key, node_val in base_workflow_value.items():
        inputs = node_val.get('inputs', {})
        for input_key, input_val in inputs.items():
            if isinstance(input_val, dict) and 'type' in input_val and 'values' in input_val:
                tuned_keys.setdefault(node_key, set()).add(input_key)
    return tuned_keys

def collect_run_input_values(run_workflows, tuned_keys):
    combined_assessments = {}
    for node_key, input_keys in tuned_keys.items():
        for input_key in input_keys:
            combined_assessments.setdefault(node_key, {})[input_key] = set()
            for workflow in run_workflows:
                if node_key in workflow and 'inputs' in workflow[node_key]:
                    if input_key in workflow[node_key]['inputs']:
                        combined_assessments[node_key][input_key].add(
                            str(workflow[node_key]['inputs'][input_key])
                        )
    return combined_assessments

def combine_differing_inputs(run_workflows, base_workflow):
    tuned_keys = extract_tuned_input_keys(base_workflow)
    combined_assessments = collect_run_input_values(run_workflows, tuned_keys)
    return combined_assessments


def convert_and_adjust_values(base_workflow, good_tune_params, bad_tune_params):
    base_workflow_value = extract_base_workflow(base_workflow)

    for node_key, node_data in base_workflow_value.items():
        inputs = node_data.get('inputs', {})
        for input_key in list(inputs.keys()):
            if ((node_key in good_tune_params and input_key in good_tune_params[node_key]) or 
                (node_key in bad_tune_params and input_key in bad_tune_params[node_key])):
                
                good_set = good_tune_params.get(node_key, {}).get(input_key, set())
                bad_set = bad_tune_params.get(node_key, {}).get(input_key, set())

                print(f"Good set for {node_key}:{input_key} -> {good_set}")
                print(f"Bad set for {node_key}:{input_key} -> {bad_set}")

                good_nums = [to_num(v) for v in good_set if to_num(v) is not None]
                bad_nums  = [to_num(v) for v in bad_set if to_num(v) is not None]

                current_range = inputs[input_key].get("values", None)
                if not (current_range and len(current_range) == 2):
                    continue
                try:
                    base_lower = float(current_range[0])
                    base_upper = float(current_range[1])
                except ValueError:
                    continue

                if good_nums and bad_nums and inputs[input_key]['type'] == 'range':
                    msg = update_range_from_good_bad(
                        inputs, input_key, base_lower, base_upper, good_nums, bad_nums
                    )
                    print(f"Updated {node_key}:{input_key} to {msg}", flush=True)
                else:
                    msg = update_range_fallback(inputs, input_key, good_set, bad_set)
                    print(f"Updated {node_key}:{input_key} using fallback: {msg}", flush=True)
    return base_workflow_value


def update_ranges_by_quality_control(run_workflow_ids, base_workflow, threshold, db):
    good_workflows, bad_workflows = sort_workflows(run_workflow_ids, threshold, db)
    
    if good_workflows:
        print(f"num good workflows: {len(good_workflows)}", flush=True)
        good_tune_vals = combine_differing_inputs(good_workflows, base_workflow)
        bad_tune_vals = combine_differing_inputs(bad_workflows, base_workflow)

        print(f"good vals tuning: {good_tune_vals}", flush=True)
        print(f"bad vals tuning: {bad_tune_vals}", flush=True)

        updated_base_workflow = convert_and_adjust_values(base_workflow, good_tune_vals, bad_tune_vals)
    else:
        updated_base_workflow = extend_ranges_from_base(base_workflow)
    
    if len(updated_base_workflow.keys()) == 1 and 'value' not in updated_base_workflow:
        updated_base_workflow = {'value': updated_base_workflow}

    return updated_base_workflow
