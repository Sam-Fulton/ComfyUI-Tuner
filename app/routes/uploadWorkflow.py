from flask import Blueprint, request, jsonify
from app.utils.mongo import get_db, insert_base_workflow
from app.utils.utils import extract_and_validate_json

upload_workflow_bp = Blueprint('uploadWorkflow', __name__)

@upload_workflow_bp.route('/api/uploadWorkflow', methods=['POST'])
def upload_workflow():  
    try:
        request_payload, error_response, status_code = extract_and_validate_json(request)
        if error_response:
            return error_response, status_code
        
        try:
            insert_base_workflow(db=get_db(), workflow_data=request_payload)
        except Exception as db_error:
            return jsonify({"error": "Failed to insert workflow into database: " + str(db_error)}), 500

        return jsonify({"message": "Workflow successfully added"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def data_error_message():
    return jsonify({"error": "Invalid Content uploaded, please upload a valid ComfyUI api workflow"})
