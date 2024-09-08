import pytest
from flask import Flask
from app.app import create_app

def test_create_app():
    app = create_app(comfyui_address='127.0.0.1:8188')
    assert isinstance(app, Flask)
    assert app.config['COMFYUI_ADDRESS'] == '127.0.0.1:8188'

def test_blueprints_registered():
    app = create_app(comfyui_address='127.0.0.1:8188')
    expected_blueprints = [
        'getOutputs',
        'getBaseWorkflows',
        'getRunWorkflows',
        'qualityCheck',
        'rerun',
        'startRun',
        'uploadWorkflow',
        'static_files',
        'getRunWorkflowsByBaseID',
        'getQualityAssessmentByRunWorkflow',
    ]
    registered_blueprints = list(app.blueprints.keys())
    assert set(expected_blueprints).issubset(set(registered_blueprints))

@pytest.fixture
def client():
    app = create_app(comfyui_address='127.0.0.1:8188')
    return app.test_client()

def test_routes_exist(client):
    routes = [
        '/api/getOutputs',
        '/api/getBaseWorkflows',
        '/api/getRunWorkflows',
        '/api/qualityCheck',
        '/api/rerun_workflow',
        '/api/startRun',
        '/api/uploadWorkflow',
        '/api/outputs',
        '/api/getRunWorkflowsByBaseID',
        '/api/getQualityAssessmentByRunWorkflow',
    ]
    
    for route in routes:
        response = client.post(route)
        assert response.status_code != 404, f"Route {route} is not registered."
