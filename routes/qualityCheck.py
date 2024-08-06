from flask import Blueprint, request, jsonify
from ..utils.mongo import insert_quality_review, get_db
from ..utils.qualityAssessment import QualityAssessment

quality_check_bp = Blueprint('qualityCheck', __name__)

@quality_check_bp.route('/api/qualityCheck', methods=['POST'])
def quality_check():
    try:
        image_quality = request.json
        
        db = get_db()
        
        quality_assessment = QualityAssessment(
            workflow_id=image_quality['run_workflow_id'],
            path=image_quality['path'],
            quality_assessment=image_quality['quality_assessment']
        )

        insert_quality_review(db=db, quality_assessment=quality_assessment)

        return jsonify({"message": "Quality assessment for image saved"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400      
    except Exception as e:
        return jsonify({"error": str(e)}), 500