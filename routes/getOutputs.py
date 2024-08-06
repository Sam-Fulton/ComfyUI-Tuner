from flask import Blueprint, request, jsonify, current_app
from ..utils.mongo import find_outputs_by_workflow_id, get_db, find_workflow

get_outputs_bp = Blueprint('getOutputs', __name__)

@get_outputs_bp.route('/api/getOutputs', methods=['GET'])
def get_outputs():
    try:
        workflow_id = request.json['workflow_id']
        db = get_db()
        workflow = find_workflow(db=db, workflow_id=workflow_id)
        if workflow is None:
            return jsonify({"error": f"There was no workflow found with id : {workflow_id}"}), 400
        
        outputs = find_outputs_by_workflow_id(db=db, workflow_id=workflow_id)

        if outputs is None:
            return jsonify({"error": f"There was no outputs found for workflow: {workflow_id}"}), 400

        return outputs, 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500