from flask import Blueprint, request, jsonify
from app.utils.mongo import get_db, find_base_workflow
from app.utils.tuneParams import update_ranges_by_quality_control

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
        if not base_workflow:
            return jsonify({"error": "Base workflow not found"}), 400

        updated_base_workflow = update_ranges_by_quality_control(run_workflow_ids, base_workflow, threshold, db)

        response = {'updated_workflow': updated_base_workflow}

        print(f"RESPONSE {response}")
        
        return jsonify(response), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
