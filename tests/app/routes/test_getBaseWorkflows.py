import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes.getBaseWorkflows import get_base_workflows_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(get_base_workflows_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_base_workflows_success(client):
    with patch('app.routes.getBaseWorkflows.get_db') as mock_get_db, \
         patch('app.routes.getBaseWorkflows.fetch_base_workflows') as mock_fetch_base_workflows, \
         patch('app.routes.getBaseWorkflows.convert_objectid_to_str') as mock_convert_objectid_to_str:
        
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_fetch_base_workflows.return_value = [{'workflow_data': 'data'}]
        mock_convert_objectid_to_str.side_effect = lambda x: x
        
        response = client.get('/api/getBaseWorkflows')
        
        assert response.status_code == 200
        assert response.json == {
            "workflows": [{'workflow_data': 'data'}]
        }

def test_get_base_workflows_db_failure(client):
    with patch('app.routes.getBaseWorkflows.get_db', side_effect=Exception("DB connection error")):
        response = client.get('/api/getBaseWorkflows')
        
        assert response.status_code == 500
        assert response.json == {"error": "DB connection error"}

def test_get_base_workflows_fetch_failure(client):
    with patch('app.routes.getBaseWorkflows.get_db') as mock_get_db, \
         patch('app.routes.getBaseWorkflows.fetch_base_workflows', side_effect=Exception("Fetch error")):
        
        mock_get_db.return_value = MagicMock()
        response = client.get('/api/getBaseWorkflows')
        
        assert response.status_code == 500
        assert response.json == {"error": "Fetch error"}
