from flask import Blueprint, jsonify, request
from app.utils.mongo import get_db, find_base_workflow
from app.utils.tuneParams import update_ranges_by_quality_control
from app.utils.utils import extract_and_validate_json

rerun_bp = Blueprint('rerun', __name__)

@rerun_bp.route('/api/rerun_workflow', methods=['POST'])
def rerun():
    try:
        request_payload, error_response, status_code = extract_and_validate_json(request)
        if error_response:
            return error_response, status_code
        required_keys = ['base_workflow_id', 'run_workflow_ids', 'threshold']
        if not all(key in request_payload for key in required_keys):
            return jsonify({"error": "Missing required data in the JSON payload"}), 400

        base_workflow_id = request_payload['base_workflow_id']
        run_workflow_ids = request_payload['run_workflow_ids']
        threshold = request_payload['threshold']
        
        db = get_db()
        base_workflow = find_base_workflow(db, base_workflow_id)
        if not base_workflow:
            return jsonify({"error": "Base workflow not found"}), 400

        updated_base_workflow = update_ranges_by_quality_control(run_workflow_ids, base_workflow, threshold, db)
        
        return jsonify({'updated_workflow': updated_base_workflow}), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500