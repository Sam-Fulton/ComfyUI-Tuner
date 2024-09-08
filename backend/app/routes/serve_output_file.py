import os
from flask import Blueprint, send_from_directory, request, jsonify
from app.utils.utils import extract_and_validate_json

static_files_bp = Blueprint('static_files', __name__)

@static_files_bp.route('/api/outputs', methods=['POST'])
def serve_output_file():
    try:
        request_payload, error_response, status_code = extract_and_validate_json(request)
        if error_response:
            return error_response, status_code

        if 'path' not in request_payload:
            return jsonify({"error": "Path not provided"}), 400
        
        filepath = request_payload['path']
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        
        if not os.path.exists(filepath):
            return jsonify({"error": "Invalid path"}), 400
        
        return send_from_directory(directory, filename)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
