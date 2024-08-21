from flask import Blueprint, jsonify, request
from app.utils.mongo import get_db, fetch_run_workflows_by_base_workflow_id
from app.utils.utils import convert_objectid_to_str, extract_and_validate_json

get_run_workflows_by_base_id_bp = Blueprint('getRunWorkflowsByBaseID', __name__)

@get_run_workflows_by_base_id_bp.route('/api/getRunWorkflowsByBaseID', methods=['POST'])
def get_run_workflows_by_base_id():
    try:
        db = get_db()
        request_payload, error_response, status_code = extract_and_validate_json(request)
        if error_response:
            return error_response, status_code
        
        if 'base_workflow_id' not in request_payload:
            return jsonify({"error": "No base_workflow_id was supplied"}), 400
        
        base_workflow_id = request_payload['base_workflow_id']
        workflows = fetch_run_workflows_by_base_workflow_id(db, base_workflow_id)
        workflows = [convert_objectid_to_str(workflow) for workflow in workflows]
        workflows = {"run_workflows" : workflows}
        return jsonify(workflows), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500