import argparse
import os
from flask import Flask
from flask_cors import CORS
from app.routes.getOutputs import get_outputs_bp
from app.routes.getBaseWorkflows import get_base_workflows_bp
from app.routes.getRunWorkflows import get_run_workflows_bp
from app.routes.qualityCheck import quality_check_bp
from app.routes.rerun import rerun_bp
from app.routes.startRun import start_run_bp
from app.routes.uploadWorkflow import upload_workflow_bp
from app.routes.serve_output_file import static_files_bp
from app.routes.getRunWorkflowsByBaseID import get_run_workflows_by_base_id_bp
from app.routes.getQualityAssessmentByRunWorkflow import get_quality_assessment_by_run_workflow_bp

def create_app(comfyui_address):
    app = Flask(__name__)
    app.config['COMFYUI_ADDRESS'] = comfyui_address
    CORS(app)
    register_blueprints(app)

    return app

def register_blueprints(app):
    app.register_blueprint(get_outputs_bp)
    app.register_blueprint(get_base_workflows_bp)
    app.register_blueprint(get_run_workflows_bp)
    app.register_blueprint(quality_check_bp)
    app.register_blueprint(rerun_bp)
    app.register_blueprint(start_run_bp)
    app.register_blueprint(upload_workflow_bp)
    app.register_blueprint(static_files_bp)
    app.register_blueprint(get_run_workflows_by_base_id_bp)
    app.register_blueprint(get_quality_assessment_by_run_workflow_bp)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--host', default=os.getenv('HOST', '0.0.0.0'), type=str, help='Host address to run the Tuner app on')
    parser.add_argument('-p', '--port', default=int(os.getenv('PORT', 5000)), type=int, help='Port to run the Tuner app on')
    parser.add_argument('-s', '--comfyui-address', default=os.getenv('COMFYUI_ADDRESS', '127.0.0.1:8188'), type=str, help='Server address of ComfyUI instance')
    return parser.parse_args()

def main():
    args = parse_args()
    app = create_app(args.comfyui_address)
    app.run(host=args.host, port=args.port, debug=True)

if __name__ == '__main__':
    main()
