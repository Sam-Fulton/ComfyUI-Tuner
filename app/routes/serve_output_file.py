from flask import Blueprint, send_from_directory, request, jsonify
import os

static_files_bp = Blueprint('static_files', __name__)

@static_files_bp.route('/api/outputs', methods=['POST'])
def serve_output_file():
    data = request.get_json()
    if not data or 'path' not in data:
        return jsonify({"error": "Path not provided"}), 400
    
    filepath = data['path']
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    
    if not os.path.exists(filepath):
        return jsonify({"error": "Invalid path"}), 400
    
    try:
        return send_from_directory(directory, filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
