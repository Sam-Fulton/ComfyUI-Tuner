from flask import Blueprint, jsonify, request
from app.utils.mongo import get_db, find_quality_assessments_by_run_workflow_ids
from app.utils.utils import extract_and_validate_json

get_quality_assessment_by_run_workflow_bp = Blueprint('getQualityAssessmentByRunWorkflow', __name__)

@get_quality_assessment_by_run_workflow_bp.route('/api/getQualityAssessmentByRunWorkflow', methods=['POST'])
def get_quality_assessment_by_run_workflow():
    try:
        request_payload, error_response, status_code = extract_and_validate_json(request)

        if error_response:
            return error_response, status_code

        if 'run_workflow_ids' not in request_payload:
            return jsonify({"error": "No valid run_workflow_id was supplied"}), 400

        db = get_db()
        run_workflow_ids = request_payload['run_workflow_ids']
        quality_assessments = find_quality_assessments_by_run_workflow_ids(db, run_workflow_ids)

        return jsonify({"quality_assessments": quality_assessments}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
