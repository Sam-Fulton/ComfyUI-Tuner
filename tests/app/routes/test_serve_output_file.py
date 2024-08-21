import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app.routes.serve_output_file import static_files_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(static_files_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.routes.serve_output_file.os.path.exists')
@patch('app.routes.serve_output_file.send_from_directory')
def test_serve_output_file_success(mock_send_from_directory, mock_path_exists, client):
    mock_path_exists.return_value = True
    mock_send_from_directory.return_value = MagicMock()

    response = client.post('/api/outputs', json={"path": "/valid/path/to/file.png"})
    
    assert response.status_code == 200
    mock_send_from_directory.assert_called_once_with('/valid/path/to', 'file.png')

@patch('app.routes.serve_output_file.os.path.exists')
def test_serve_output_file_invalid_path(mock_path_exists, client):
    mock_path_exists.return_value = False

    response = client.post('/api/outputs', json={"path": "/invalid/path/to/file.png"})
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data
    assert json_data["error"] == "Invalid path"

def test_serve_output_file_missing_path(client):
    response = client.post('/api/outputs', json={})
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data
    assert json_data["error"] == "Path not provided"

def test_serve_output_file_no_json(client):
    response = client.post('/api/outputs', data="Invalid JSON", content_type='application/json')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data
    assert json_data["error"] == "Failed to parse JSON data"

@patch('app.routes.serve_output_file.os.path.exists')
@patch('app.routes.serve_output_file.send_from_directory')
def test_serve_output_file_exception_handling(mock_send_from_directory, mock_path_exists, client):
    mock_path_exists.return_value = True
    mock_send_from_directory.side_effect = Exception("Some unexpected error")

    response = client.post('/api/outputs', json={"path": "/valid/path/to/file.png"})
    
    assert response.status_code == 500
    json_data = response.get_json()
    assert "error" in json_data
    assert json_data["error"] == "Some unexpected error"
