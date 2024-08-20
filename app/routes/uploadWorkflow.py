from flask import Blueprint, request, jsonify
from app.utils.mongo import get_db, insert_base_workflow

upload_workflow_bp = Blueprint('uploadWorkflow', __name__)

@upload_workflow_bp.route('/api/uploadWorkflow', methods=['POST'])
def upload_workflow():
    if not request.is_json:
        return data_error_message(), 400
    
    try:
        try:
            workflow_data = request.get_json()
            if workflow_data is None:
                return data_error_message(), 400
        except Exception:
            return jsonify({"error": "No valid json data was supplied"}), 400
        
        try:
            insert_base_workflow(db=get_db(), workflow_data=workflow_data)
        except Exception as db_error:
            return jsonify({"error": "Failed to insert workflow into database: " + str(db_error)}), 500

        return jsonify({"message": "Workflow successfully added"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def data_error_message():
    return jsonify({"error": "Invalid Content uploaded, please upload a valid ComfyUI api workflow"})
