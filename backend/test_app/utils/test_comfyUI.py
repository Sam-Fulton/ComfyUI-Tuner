import pytest
import json
from unittest.mock import patch, MagicMock
from app.utils.comfyUI import make_comfyUI_request, open_websocket_connection, track_progress, check_queue_status, queue_prompt

sample_run_workflow = {
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
    }
}
sample_server_address = "localhost:8188"
sample_client_id = "sample-client-id"

def setup_websocket_mock(mock_ws_connect, recv_side_effect):
    ws_instance = MagicMock()
    mock_ws_connect.return_value = ws_instance
    ws_instance.recv.side_effect = recv_side_effect
    return ws_instance

@patch('websocket.WebSocket')
@patch('uuid.uuid4')
def test_open_websocket_connection(mock_uuid, mock_websocket):
    mock_uuid.return_value = sample_client_id
    ws_instance = MagicMock()
    mock_websocket.return_value = ws_instance

    ws, client_id = open_websocket_connection(sample_server_address)

    assert client_id == sample_client_id
    ws_instance.connect.assert_called_once_with(f"ws://{sample_server_address}/ws?clientId={sample_client_id}")

@patch('app.utils.comfyUI.check_queue_status')
@patch('websocket.WebSocket.connect')
def test_track_progress_exit_on_node_none(mock_ws_connect, mock_check_queue_status):
    ws_instance = setup_websocket_mock(mock_ws_connect, [
        json.dumps({"type": "progress", "data": {"value": 1, "max": 10}}),
        json.dumps({"type": "execution_cached", "data": {"nodes": ["1"]}}),
        json.dumps({"type": "executing", "data": {"node": "1", "prompt_id": "prompt-1"}}),
        json.dumps({"type": "executing", "data": {"node": None, "prompt_id": "prompt-1"}}),
    ])

    mock_check_queue_status.side_effect = [
        {"queue_running": ["some_task"], "queue_pending": ["pending_task"]},
        {"queue_running": ["some_task"], "queue_pending": ["pending_task"]},
        {"queue_running": ["some_task"], "queue_pending": ["pending_task"]},
    ]

    track_progress(sample_run_workflow, ws_instance, "prompt-1", sample_server_address)

    assert ws_instance.recv.call_count == 4
    assert mock_check_queue_status.call_count == 3

@patch('app.utils.comfyUI.check_queue_status')
@patch('websocket.WebSocket.connect')
def test_track_progress_exit_on_prompt_executed(mock_ws_connect, mock_check_queue_status):
    ws_instance = setup_websocket_mock(mock_ws_connect, [
        json.dumps({"type": "progress", "data": {"value": 1, "max": 10}}),
        json.dumps({"type": "execution_cached", "data": {"nodes": ["1"]}}),
        json.dumps({"type": "executing", "data": {"node": "1", "prompt_id": "prompt-1"}}),
        b"Prompt executed",
    ])

    mock_check_queue_status.side_effect = [
        {"queue_running": ["some_task"], "queue_pending": ["pending_task"]},
        {"queue_running": ["some_task"], "queue_pending": ["pending_task"]},
        {"queue_running": ["some_task"], "queue_pending": ["pending_task"]},
        {"queue_running": [], "queue_pending": []},
    ]

    track_progress(sample_run_workflow, ws_instance, "prompt-1", sample_server_address)

    assert ws_instance.recv.call_count == 4
    assert mock_check_queue_status.call_count == 3

@patch('app.utils.comfyUI.check_queue_status')
@patch('websocket.WebSocket.connect')
def test_track_progress_exit_on_empty_queue(mock_ws_connect, mock_check_queue_status):
    ws_instance = setup_websocket_mock(mock_ws_connect, [
        json.dumps({"type": "progress", "data": {"value": 1, "max": 10}}),
        json.dumps({"type": "execution_cached", "data": {"nodes": ["1"]}}),
    ])

    mock_check_queue_status.side_effect = [
        {"queue_running": ["some_task"], "queue_pending": ["pending_task"]},
        {"queue_running": [], "queue_pending": []},
    ]

    track_progress(sample_run_workflow, ws_instance, "prompt-1", sample_server_address)

    assert ws_instance.recv.call_count == 2
    assert mock_check_queue_status.call_count == 2

@patch('urllib.request.urlopen')
def test_check_queue_status(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"queue_running": [], "queue_pending": []}).encode('utf-8')
    mock_urlopen.return_value = mock_response

    queue_info = check_queue_status(sample_server_address)

    assert queue_info == {"queue_running": [], "queue_pending": []}

@patch('urllib.request.urlopen')
def test_queue_prompt(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"prompt_id": "prompt-1"}).encode('utf-8')
    mock_urlopen.return_value = mock_response

    prompt_id = queue_prompt(sample_run_workflow, sample_client_id, sample_server_address)

    assert prompt_id == {"prompt_id": "prompt-1"}

@patch('app.utils.comfyUI.queue_prompt')
@patch('app.utils.comfyUI.open_websocket_connection')
def test_make_comfyUI_request(mock_open_ws, mock_queue_prompt):
    ws_instance = MagicMock()
    mock_open_ws.return_value = (ws_instance, sample_client_id)
    mock_queue_prompt.return_value = "prompt-1"

    with patch('app.utils.comfyUI.track_progress') as mock_track_progress:
        make_comfyUI_request(sample_run_workflow, sample_server_address)
        mock_track_progress.assert_called_once_with(sample_run_workflow, ws_instance, "prompt-1", sample_server_address)
        ws_instance.close.assert_called_once()
