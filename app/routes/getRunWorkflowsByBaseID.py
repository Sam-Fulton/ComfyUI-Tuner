from flask import Blueprint, jsonify, request
from utils.mongo import get_db, fetch_run_workflows_by_base_workflow_id
from utils.utils import convert_objectid_to_str

get_run_workflows_by_base_id_bp = Blueprint('getRunWorkflowsByBaseID', __name__)

@get_run_workflows_by_base_id_bp.route('/api/getRunWorkflowsByBaseID', methods=['POST'])
def get_run_workflows_by_base_id():
    try:
        db = get_db()
        base_workflow_id = request.json['base_workflow_id']
        workflows = fetch_run_workflows_by_base_workflow_id(db, base_workflow_id)
        workflows = [convert_objectid_to_str(workflow) for workflow in workflows]
        workflows = {"run_workflows" : workflows}
        return jsonify(workflows), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500