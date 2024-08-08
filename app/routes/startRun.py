from flask import Blueprint, request, jsonify, current_app
from utils.comfyUI import make_comfyUI_request
from utils.mongo import insert_outputs, get_db, insert_run_workflow
from utils.outputs import Outputs
from utils.tuneParams import label_workflow_for_random_sampling, prepare_run_workflow
from utils.utils import get_output_paths, new_outputs

start_run_bp = Blueprint('startRun', __name__)

@start_run_bp.route('/api/startRun', methods=['POST'])
def start_run():
    if not request.is_json:
        return jsonify({"error": "No valid run data was supplied, please upload a workflow/prompt"}), 400
    try:
        
        base_workflow = request.json['base_workflow']

        num_runs = request.json['num_runs']

        results = []
        ##TODO Check if comfy server is running, if not start
        
        print("got request")

        db = get_db()
        before_outputs = get_output_paths(base_workflow)
        
        print("output paths got", flush=True)

        base_workflow = label_workflow_for_random_sampling(base_workflow)

        print(f"workflow prepared: {base_workflow}", flush=True)

        run_workflows = [prepare_run_workflow(base_workflow) for _ in range(num_runs)]
        
        print("run workflows prepared", flush=True)

        print(len(run_workflows), flush=True)

        for run_workflow in run_workflows:
            print(f"run workflow: {run_workflow}", flush=True)
            make_comfyUI_request(run_workflow, current_app.config['COMFYUI_ADDRESS'])
            print("COMFYUI request finished", flush=True)
            after_outputs = get_output_paths(base_workflow)

            workflow_output_paths = new_outputs(before_outputs, after_outputs)

            print(f"workflow outputs: {workflow_output_paths}", flush=True)
            
            if len(workflow_output_paths) == 0:
                return jsonify({"message": "The workflow produced no output please check your workflow and try running again, or check with comfyUI", "results": results}), 200

            else: 
                run_workflow_id = insert_run_workflow(db=db, workflow_data=run_workflow)
                
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