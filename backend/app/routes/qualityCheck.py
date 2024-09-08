from flask import Blueprint, request, jsonify
from app.utils.mongo import insert_quality_review, get_db, find_quality_assessments_by_run_workflow_id_path, update_quality_assessment
from app.utils.qualityAssessment import QualityAssessment
from app.utils.utils import extract_and_validate_json

quality_check_bp = Blueprint('qualityCheck', __name__)

@quality_check_bp.route('/api/qualityCheck', methods=['POST'])
def quality_check():
    try:
        
        request_payload, error_response, status_code = extract_and_validate_json(request)
        if error_response:
            return error_response, status_code
        
        required_keys = ['run_workflow_id', 'path', 'quality_assessment']
        if not all(key in request_payload for key in required_keys):
            return jsonify({"error": "run_workflow_id, path or quality_assessment not in request"}), 400
        
        db = get_db()

        quality_assessment = QualityAssessment(
            run_workflow_id=request_payload['run_workflow_id'],
            path=request_payload['path'],
            quality_assessment=request_payload['quality_assessment']
        )

        if find_quality_assessments_by_run_workflow_id_path(db, request_payload['run_workflow_id'], request_payload['path']) != []:
            update_quality_assessment(
                db=db,             
                run_workflow_id=request_payload['run_workflow_id'],
                path=request_payload['path'],
                quality_assessment=request_payload['quality_assessment']
            )
            print("quality_assessment updated", flush=True)
        else:
            insert_quality_review(db=db, quality_assessment=quality_assessment)
            print("quality_assessment submitted", flush=True)

        return jsonify({"message": "Quality assessment for image saved"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400      
    except Exception as e:
        return jsonify({"error": str(e)}), 500