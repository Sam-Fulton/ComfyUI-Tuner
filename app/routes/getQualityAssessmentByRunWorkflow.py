from flask import Blueprint, jsonify, request
from app.utils.mongo import get_db, find_quality_assessments_by_run_workflow_ids

get_quality_assessment_by_run_workflow_bp = Blueprint('getQualityAssessmentByRunWorkflow', __name__)

@get_quality_assessment_by_run_workflow_bp.route('/api/getQualityAssessmentByRunWorkflow', methods=['POST'])
def get_quality_assessment_by_run_workflow():
    try:
        try:
            data = request.get_json()
            if data is None:
                return jsonify({"error": "No valid json data was supplied"}), 400
        except Exception:
            return jsonify({"error": "No valid json data was supplied"}), 400

        if 'run_workflow_ids' not in data:
            return jsonify({"error": "No valid run_workflow_id was supplied"}), 400

        db = get_db()
        run_workflow_ids = data['run_workflow_ids']
        quality_assessments = find_quality_assessments_by_run_workflow_ids(db, run_workflow_ids)

        return jsonify({"quality_assessments": quality_assessments}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
