from flask import Blueprint, request, jsonify
from app.utils.mongo import find_outputs_by_run_workflow_id, get_db, find_run_workflow
from app.utils.utils import extract_and_validate_json

get_outputs_bp = Blueprint('getOutputs', __name__)

@get_outputs_bp.route('/api/getOutputs', methods=['POST'])
def get_outputs():
    try:
        request_payload, error_response, status_code = extract_and_validate_json(request)
        if error_response:
            return error_response, status_code

        if 'run_workflow_id' not in request_payload:
            return jsonify({"error": "No run_workflow_id was supplied"}), 400

        run_workflow_id = request_payload['run_workflow_id']
        print(run_workflow_id, flush=True)

        db = get_db()
        workflow = find_run_workflow(db=db, run_workflow_id=run_workflow_id)
        if workflow is None:
            return jsonify({"error": f"There was no workflow found with id: {run_workflow_id}"}), 400

        print(f"workflow: {workflow}", flush=True)
        outputs = find_outputs_by_run_workflow_id(db=db, run_workflow_id=run_workflow_id)

        print(f"outputs: {outputs}", flush=True)

        if outputs is None or len(outputs) == 0:
            return jsonify({"error": f"There were no outputs found for workflow: {run_workflow_id}"}), 400

        return jsonify({"message": f"Outputs for run {run_workflow_id} retrieved", "outputs": outputs}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500