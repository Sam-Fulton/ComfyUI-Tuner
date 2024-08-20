from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from app.utils.comfyUI import make_comfyUI_request
from app.utils.mongo import insert_outputs, get_db, insert_run_workflow, update_base_workflow, find_base_workflow
from app.utils.outputs import Outputs
from app.utils.tuneParams import label_workflow_for_random_sampling, prepare_run_workflow
from app.utils.utils import get_output_paths, new_outputs

start_run_bp = Blueprint('startRun', __name__)

@start_run_bp.route('/api/startRun', methods=['POST'])
def start_run():
    if not request.is_json:
        return jsonify({"error": "No valid run data was supplied, please upload a workflow/prompt"}), 400
    try:
        
        request_payload = request.json

        db = get_db()

        base_workflow = request_payload['base_workflow']

        if "value" in base_workflow and len(base_workflow.keys()) == 1:
            base_workflow = base_workflow['value']

        if 'base_workflow_id' in request_payload:
            updated = update_base_workflow(db, base_workflow_id=request_payload['base_workflow_id'], updated_workflow_data=request_payload['base_workflow'])

            if updated:
                print("Updated workflow", flush=True)
        
        else:
            print("no workflow to update", flush=True)

        num_runs = int(request_payload['num_runs'])

        print(f'num_runs: {num_runs}')

        results = []
        ##TODO Check if comfy server is running, if not start
        
        print(base_workflow, flush=True)

        base_workflow = label_workflow_for_random_sampling(base_workflow)

        print(f"workflow prepared: {base_workflow}", flush=True)

        run_workflows = [prepare_run_workflow(base_workflow) for _ in range((num_runs))]
        
        print("run workflows prepared", flush=True)

        print(len(run_workflows), flush=True)

        group_timestamp = int(datetime.now().timestamp())
        
        for run_workflow in run_workflows:
            before_outputs = get_output_paths(base_workflow)
        
            print("output paths got", flush=True)
            
            print(f"run workflow: {run_workflow}", flush=True)
            make_comfyUI_request(run_workflow, current_app.config['COMFYUI_ADDRESS'])
            print("COMFYUI request finished", flush=True)
            after_outputs = get_output_paths(base_workflow)

            workflow_output_paths = new_outputs(before_outputs, after_outputs)

            print(f"workflow outputs: {workflow_output_paths}", flush=True)
            
            if len(workflow_output_paths) == 0:
                return jsonify({"message": "The workflow produced no output please check your workflow and try running again, or check with comfyUI", "results": results}), 200

            else: 
                run_workflow_id = insert_run_workflow(db=db, workflow_data=run_workflow, base_workflow_id=request_payload['base_workflow_id'], group_timestamp=group_timestamp)
                
                print("Run workflow saved", flush=True)

                outputs = Outputs(run_workflow_id=str(run_workflow_id), paths=workflow_output_paths)

                print(f"outputs to be inserted {outputs}", flush=True)

                output_id = insert_outputs(db=db, outputs=outputs)

                print(f"outputs inserted with id : {output_id}", flush=True)

                results.append({
                    "run_workflow_id": str(run_workflow_id),
                    "output_id": str(output_id)
                })

        print(f"results: {results}", flush=True)

        return jsonify({"message": "Workflows processed successfully", "results": results}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        response = {"error": str(e)}
        print(response)
        return jsonify({"error": str(e)}), 500