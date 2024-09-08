from flask import Blueprint, jsonify
from app.utils.mongo import fetch_base_workflows, get_db
from app.utils.utils import convert_objectid_to_str

get_base_workflows_bp = Blueprint('getBaseWorkflows', __name__)

@get_base_workflows_bp.route('/api/getBaseWorkflows', methods=['GET'])
def get_base_workflows():
    try:
        db = get_db()
        workflows = fetch_base_workflows(db)
        workflows = [convert_objectid_to_str(workflow) for workflow in workflows]
        workflows = {"workflows" : workflows}
        return jsonify(workflows), 200

    except Exception as e:
        response = {"error": str(e)}
        print(response)
        return jsonify(response), 500