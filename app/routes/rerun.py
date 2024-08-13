from flask import Blueprint, request, jsonify
from utils.mongo import get_db, find_base_workflow
from utils.tuneParams import update_ranges_by_quality_control

rerun_bp = Blueprint('rerun', __name__)

@rerun_bp.route('/api/rerun_workflow', methods=['POST'])
def rerun():
    if not request.is_json:
        return jsonify({"error": "No valid run data was supplied, please upload a workflow/prompt"}), 400
    try:
        print(request, flush=True)
        
        base_workflow_id = request.json['base_workflow_id']
        run_workflow_ids = request.json['run_workflow_ids']
        threshold = request.json['threshold']
        
        db = get_db()

        base_workflow = find_base_workflow(db, base_workflow_id)
        print(base_workflow, flush=True)
        if not base_workflow:
            return jsonify({"error": "Base workflow not found"}), 400

        updated_base_workflow = update_ranges_by_quality_control(run_workflow_ids, base_workflow, threshold, db)

        print(f"UPDATED BASE WORKFLOW {updated_base_workflow}", flush=True)

        payload = {'updated_workflow': updated_base_workflow}

        return jsonify(payload), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
