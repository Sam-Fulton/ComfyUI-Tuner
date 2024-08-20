from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from app.utils.comfyUI import make_comfyUI_request
from app.utils.mongo import insert_outputs, get_db, insert_run_workflow, update_base_workflow, find_base_workflow
from app.utils.outputs import Outputs
from app.utils.tuneParams import label_workflow_for_random_sampling, prepare_run_workflow
from app.utils.utils import get_output_paths, new_outputs, extract_and_validate_json

start_run_bp = Blueprint('startRun', __name__)

def handle_base_workflow(request_payload, db):
    base_workflow = request_payload.get('base_workflow')
    if not base_workflow:
        return None, jsonify({"error": "Base workflow is missing"}), 400

    if "value" in base_workflow and len(base_workflow.keys()) == 1:
        base_workflow = base_workflow['value']

    if 'base_workflow_id' in request_payload:
        updated = update_base_workflow(db, base_workflow_id=request_payload['base_workflow_id'], updated_workflow_data=request_payload['base_workflow'])
        if updated:
            print("Updated workflow", flush=True)
        else:
            print("No workflow to update", flush=True)
    else:
        print("No base_workflow_id provided, skipping update", flush=True)

    return base_workflow, None, None

def prepare_workflows(base_workflow, num_runs):
    base_workflow = label_workflow_for_random_sampling(base_workflow)
    print(f"workflow prepared: {base_workflow}", flush=True)
    run_workflows = [prepare_run_workflow(base_workflow) for _ in range(num_runs)]
    print("run workflows prepared", flush=True)
    return run_workflows

def process_run_workflow(run_workflow, base_workflow, db, request_payload, group_timestamp):
    before_outputs = get_output_paths(base_workflow)
    print("output paths got", flush=True)

    make_comfyUI_request(run_workflow, current_app.config['COMFYUI_ADDRESS'])
    print("COMFYUI request finished", flush=True)

    after_outputs = get_output_paths(base_workflow)
    workflow_output_paths = new_outputs(before_outputs, after_outputs)

    if not workflow_output_paths:
        return None, jsonify({"message": "The workflow produced no output. Please check your workflow and try again or check with ComfyUI.", "results": []}), 200

    run_workflow_id = insert_run_workflow(db=db, workflow_data=run_workflow, base_workflow_id=request_payload['base_workflow_id'], group_timestamp=group_timestamp)
    outputs = Outputs(run_workflow_id=str(run_workflow_id), paths=workflow_output_paths)
    output_id = insert_outputs(db=db, outputs=outputs)

    return {"run_workflow_id": str(run_workflow_id), "output_id": str(output_id)}, None, None

@start_run_bp.route('/api/startRun', methods=['POST'])
def start_run():
    try:
        request_payload, error_response, status_code = extract_and_validate_json()
        if error_response:
            return error_response, status_code
        
        db = get_db()

        base_workflow, error_response, status_code = handle_base_workflow(request_payload, db)
        if error_response:
            return error_response, status_code

        num_runs = int(request_payload.get('num_runs', 0))
        if num_runs <= 0:
            return jsonify({"error": "Number of runs must be greater than zero"}), 400

        print(f'num_runs: {num_runs}', flush=True)
        
        run_workflows = prepare_workflows(base_workflow, num_runs)
        
        group_timestamp = int(datetime.now().timestamp())
        results = []

        for run_workflow in run_workflows:
            result, error_response, status_code = process_run_workflow(run_workflow, base_workflow, db, request_payload, group_timestamp)
            if error_response:
                return error_response, status_code
            results.append(result)

        return jsonify({"message": "Workflows processed successfully", "results": results}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        response = {"error": str(e)}
        print(response, flush=True)
        return jsonify(response), 500
