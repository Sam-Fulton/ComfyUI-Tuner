import pytest
from flask import Flask, request, json
from unittest.mock import patch, MagicMock
from bson import ObjectId
from app.utils.utils import get_output_paths, new_outputs, convert_objectid_to_str, extract_and_validate_json

sample_workflow = {
    "1": {
        "class_type": "SaveImage",
        "inputs": {
            "filename": "image_1.png"
        }
    },
    "2": {
        "class_type": "SaveVideo",
        "inputs": {
            "filename": "video_1.mp4"
        }
    },
    "3": {
        "class_type": "Transform",
        "inputs": {
            "input_file": "image_2.png"
        }
    }
}

@pytest.fixture
def mock_os_path_exists():
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True
        yield mock_exists

@pytest.fixture
def mock_os_walk():
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ("/app/ComfyUI/output", [], ["image_1.png", "video_1.mp4"])
        ]
        yield mock_walk

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_output_paths(mock_os_path_exists, mock_os_walk):
    output_files = get_output_paths(sample_workflow)
    assert len(output_files) == 2
    assert "/app/ComfyUI/output/image_1.png" in output_files
    assert "/app/ComfyUI/output/video_1.mp4" in output_files

def test_get_output_paths_no_save_class(mock_os_path_exists, mock_os_walk):
    no_save_workflow = {
        "1": {
            "class_type": "Transform",
            "inputs": {
                "input_file": "image_2.png"
            }
        }
    }
    output_files = get_output_paths(no_save_workflow)
    assert len(output_files) == 0

def test_new_outputs():
    before = ["/app/ComfyUI/output/image_1.png"]
    after = ["/app/ComfyUI/output/image_1.png", "/app/ComfyUI/output/video_1.mp4"]
    new_files = new_outputs(before, after)
    assert len(new_files) == 1
    assert "/app/ComfyUI/output/video_1.mp4" in new_files

def test_convert_objectid_to_str():
    object_id = ObjectId()
    data = {
        "key1": object_id,
        "key2": [
            {"nested_key": object_id},
            ObjectId()
        ]
    }
    converted = convert_objectid_to_str(data)
    assert converted["key1"] == str(object_id)
    assert converted["key2"][0]["nested_key"] == str(object_id)
    assert isinstance(converted["key2"][1], str)

def test_extract_and_validate_json_success(app):
    with app.test_request_context(json={"key": "value"}):
        result, error_response, status_code = extract_and_validate_json(request)
        assert result == {"key": "value"}
        assert error_response is None
        assert status_code is None

def test_extract_and_validate_json_invalid_json(app):
    with app.test_request_context(data="{invalid json}", content_type="application/json"):
        with patch.object(request, 'get_json', side_effect=ValueError("Invalid JSON")):
            result, error_response, status_code = extract_and_validate_json(request)
            assert result is None
            assert error_response.json == {"error": "Failed to parse JSON data"}
            assert status_code == 400

def test_extract_and_validate_json_no_payload(app):
    with app.test_request_context():
        with patch.object(request, 'get_json', return_value=None):
            result, error_response, status_code = extract_and_validate_json(request)
            assert result is None
            assert error_response.json == {"error": "No valid JSON data was supplied"}
            assert status_code == 400
