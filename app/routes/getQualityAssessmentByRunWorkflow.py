from flask import Blueprint, jsonify, request
from app.utils.mongo import get_db, find_quality_assessments_by_run_workflow_ids

get_quality_assessment_by_run_workflow_bp = Blueprint('getQualityAssessmentByRunWorkflow', __name__)

@get_quality_assessment_by_run_workflow_bp.route('/api/getQualityAssessmentByRunWorkflow', methods=['POST'])
def get_quality_assessment_by_run_workflow():
    if not request.is_json:
        return jsonify({"error": "No valid json data was supplied"}), 400
    try:
        db = get_db()
        
        print(request.json, flush=True)
        if 'run_workflow_ids' not in request.json:
            return jsonify({"error": "No valid run_workflow_id was supplied"}), 400
        

        run_workflow_ids = request.json['run_workflow_ids']


        quality_assessments = find_quality_assessments_by_run_workflow_ids(db, run_workflow_ids)

        response = {"quality_assessments" : quality_assessments}
        print(response, flush=True)
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500