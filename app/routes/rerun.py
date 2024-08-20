from flask import Blueprint, jsonify, request
from app.utils.mongo import get_db, find_base_workflow
from app.utils.tuneParams import update_ranges_by_quality_control

rerun_bp = Blueprint('rerun', __name__)

@rerun_bp.route('/api/rerun_workflow', methods=['POST'])
def rerun():
    try:
        try:
            data = request.get_json()
            if data is None:
                return jsonify({"error": "No valid run data was supplied, please upload a workflow/prompt"}), 400
        except Exception:
            return jsonify({"error": "No valid run data was supplied, please upload a workflow/prompt"}), 400

        if 'base_workflow_id' not in data or 'run_workflow_ids' not in data or 'threshold' not in data:
            return jsonify({"error": "Missing required data in the JSON payload"}), 400

        base_workflow_id = data['base_workflow_id']
        run_workflow_ids = data['run_workflow_ids']
        threshold = data['threshold']
        
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