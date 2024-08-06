from flask import Blueprint, request, jsonify, current_app
from ..utils.comfyUI import make_comfyUI_request

from ..utils.mongo import insert_outputs, get_db, insert_workflow
from ..utils.outputs import Outputs

start_run_bp = Blueprint('startRun', __name__)

@start_run_bp.route('/api/startRun', methods=['GET'])
def start_run():
    if not request.is_json:
        return jsonify({"error": "No valid run data was supplied, please upload a workflow/prompt"}), 400
    try:
        workflows = request.get_json()
        results = []
        ##TODO Check if comfy server is running, if not start
        
        db = get_db()
        before_outputs = get_output_paths()
        for workflow in workflows:
            prompt_result = make_comfyUI_request(workflow, current_app.config['COMFYUI_ADDRESS'])
            workflow_id = insert_workflow(db=db, workflow_data=workflow)
            after_outputs = get_output_paths()

            workflow_output_paths = new_outputs(before_outputs, after_outputs)
            outputs = Outputs(workflow_id=str(workflow_id), paths=workflow_output_paths)
            output_id = insert_outputs(db=db, outputs=outputs)
            results.append({
                "workflow_id": str(workflow_id),
                "output_id": str(output_id),
                "prompt_result": prompt_result
            })

        return jsonify({"message": "Workflows processed successfully", "results": results}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
            
def get_output_paths(workflow):
    ##TODO return all possible output locations, (any nodes that contain save as class or param)
    pass

def new_outputs(before_outputs, after_outputs):
    return list(set(after_outputs) - set(before_outputs))