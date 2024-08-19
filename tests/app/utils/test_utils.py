import pytest
from unittest.mock import patch
from bson import ObjectId
from app.utils.utils import get_output_paths, new_outputs, convert_objectid_to_str

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

def test_get_output_paths(mock_os_path_exists, mock_os_walk):
    output_files = get_output_paths(sample_workflow)

    print(output_files)
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
