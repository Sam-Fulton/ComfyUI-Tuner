from routes.home import home_bp
from routes.getOutputs import get_outputs_bp
from routes.getBaseWorkflows import get_base_workflows_bp
from routes.getRunWorkflows import get_run_workflows_bp
from routes.qualityCheck import quality_check_bp
from routes.rerun import rerun_bp
from routes.startRun import start_run_bp
from routes.uploadWorkflow import upload_workflow_bp
from routes.serve_output_file import static_files_bp
from routes.getRunWorkflowsByBaseID import get_run_workflows_by_base_id_bp
from routes.getQualityAssessmentByRunWorkflow import get_quality_assessment_by_run_workflow_bp

def register_blueprints(app):
    app.register_blueprint(home_bp)
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
