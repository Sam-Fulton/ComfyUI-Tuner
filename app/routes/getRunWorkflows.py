from flask import Blueprint, jsonify
from utils.mongo import fetch_run_workflows, get_db
from utils.utils import convert_objectid_to_str

get_run_workflows_bp = Blueprint('getRunWorkflows', __name__)

@get_run_workflows_bp.route('/api/getRunWorkflows', methods=['GET'])
def get_run_workflows():
    try:
        db = get_db()
        workflows = fetch_run_workflows(db)
        workflows = [convert_objectid_to_str(workflow) for workflow in workflows]
        workflows = {"workflows" : workflows}
        return jsonify(workflows), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500