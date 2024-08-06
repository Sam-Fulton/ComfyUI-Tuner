from flask import Blueprint, request, jsonify, current_app
from ..utils.comfyUI import make_comfyUI_request

from ..utils.mongo import insert_outputs, get_db, insert_run_workflow
from ..utils.outputs import Outputs
from ..utils.tuneParams import label_workflow_for_random_sampling, prepare_run_workflow
from ..utils.utils import get_output_paths, new_outputs

start_run_bp = Blueprint('startRun', __name__)

@start_run_bp.route('/api/startRun', methods=['GET'])
def start_run():
    if not request.is_json:
        return jsonify({"error": "No valid run data was supplied, please upload a workflow/prompt"}), 400
    try:
        base_workflow = request['base_workflow']
        num_runs = request['num_runs']

        results = []
        ##TODO Check if comfy server is running, if not start
        
        db = get_db()
        before_outputs = get_output_paths()

        base_workflow = label_workflow_for_random_sampling(base_workflow)

        run_workflows = [prepare_run_workflow(base_workflow) for _ in range(num_runs)]

        for run_workflow in run_workflows:
            prompt_result = make_comfyUI_request(run_workflow, current_app.config['COMFYUI_ADDRESS'])
            run_workflow_id = insert_run_workflow(db=db, workflow_data=run_workflow)
            after_outputs = get_output_paths()

            workflow_output_paths = new_outputs(before_outputs, after_outputs)
            outputs = Outputs(workflow_id=str(run_workflow_id), paths=workflow_output_paths)
            output_id = insert_outputs(db=db, outputs=outputs)
            results.append({
                "run_workflow_id": str(run_workflow_id),
                "output_id": str(output_id),
                "prompt_result": prompt_result
            })

        return jsonify({"message": "Workflows processed successfully", "results": results}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500