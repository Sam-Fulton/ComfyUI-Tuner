from flask import Blueprint, request, jsonify, current_app
from utils.comfyUI import make_comfyUI_request
from utils.mongo import insert_outputs, get_db, insert_run_workflow, find_base_workflow, find_quality_assessment
from utils.outputs import Outputs
from utils.tuneParams import label_workflow_for_random_sampling, prepare_run_workflow
from utils.tuneParams import update_ranges_by_quality_control
from utils.utils import get_output_paths, new_outputs

rerun_bp = Blueprint('rerun', __name__)

@rerun_bp.route('/api/rerun', methods=['POST'])
def rerun():
    if not request.is_json:
        return jsonify({"error": "No valid run data was supplied, please upload a workflow/prompt"}), 400
    try:
        data = request.get_json()
        base_workflow_id = data.json['base_workflow_id']
        run_workflow_ids = data.json['run_workflow_ids']
        threshold = data.json['threshold']
        num_runs = data.json['num_runs']

        db = get_db()

        base_workflow = find_base_workflow(db, base_workflow_id)
        if not base_workflow:
            return jsonify({"error": "Base workflow not found"}), 404
    
        updated_base_workflow = update_ranges_by_quality_control(run_workflow_ids, base_workflow, threshold, db)

        labeled_base_workflow = label_workflow_for_random_sampling(updated_base_workflow)

        run_workflows = [prepare_run_workflow(labeled_base_workflow) for _ in range(num_runs)]

        results = []
        before_outputs = get_output_paths()

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
