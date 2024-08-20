from flask import Blueprint, request, jsonify
from app.utils.mongo import get_db, insert_base_workflow

upload_workflow_bp = Blueprint('uploadWorkflow', __name__)

@upload_workflow_bp.route('/api/uploadWorkflow', methods=['POST'])
def upload_workflow():
    if not request.is_json:
        return data_error_message(), 400
    
    try:
        workflow_data = request.get_json()
        print(workflow_data)
        insert_base_workflow(db=get_db(), workflow_data=workflow_data)
        return jsonify({"message": "Workflow successfully added"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def data_error_message():
    return jsonify({"error": "Invalid Content uploaded, please upload a valid ComfyUI api workflow"})