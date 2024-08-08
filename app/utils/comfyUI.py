import requests
import websocket
import uuid
import json
import urllib.request
import re

def make_comfyUI_request(run_workflow, server_address):
    try:
        print("attempting to connect", flush=True)
        print(f"ComfyUI Server address: {server_address}", flush=True)
        ws, client_id = open_websocket_connection(server_address)
        if not ws:
            raise ConnectionError(f"Failed to connect to the WebSocket server at {server_address}")

        prompt_id = queue_prompt(run_workflow, client_id, server_address)
        track_progress(run_workflow, ws, prompt_id, server_address)
        ws.close()
        
        print("Prompt/workflow finsihed executing")

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    except Exception as e:
        raise SystemExit(e)

def open_websocket_connection(server_address):
    client_id = str(uuid.uuid4())
    ws = None
    try:
        print("Attempting to connect to WebSocket server", flush=True)
        ws = websocket.WebSocket()
        address = f"ws://{server_address}/ws?clientId={client_id}"
        print(f"address: {address}")
        ws.connect(address)
        print(f"Connected to WebSocket server with client ID: {client_id}", flush=True)
    except websocket.WebSocketConnectionClosedException as e:
        print(f"WebSocket connection closed: {e}", flush=True)
    except websocket.WebSocketException as e:
        print(f"WebSocket exception: {e}", flush=True)
    except Exception as e:
        print(f"Failed to connect to WebSocket server at {server_address}: {e}", flush=True)
        return None, client_id
    return ws, client_id


def track_progress(prompt, ws, prompt_id, server_address):
    node_ids = list(prompt.keys())
    finished_nodes = []

    prompt_executed_pattern = re.compile(r'\s*prompt\s+executed\s*', re.IGNORECASE)

    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'progress':
                data = message['data']
                current_step = data['value']
                print('In K-Sampler -> Step:', current_step, 'of:', data['max'], flush=True)
            elif message['type'] == 'execution_cached':
                data = message['data']
                for itm in data['nodes']:
                    if itm not in finished_nodes:
                        finished_nodes.append(itm)
                        print('Progress:', len(finished_nodes), '/', len(node_ids), 'Tasks done', flush=True)
            elif message['type'] == 'executing':
                data = message['data']
                if data['node'] not in finished_nodes:
                    finished_nodes.append(data['node'])
                    print('Progress:', len(finished_nodes), '/', len(node_ids), 'Tasks done', flush=True)
                    
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break

        elif isinstance(out, bytes):
            message = out.decode('utf-8')
            if re.search(prompt_executed_pattern, message):
                print("Prompt executed")
                break
        else:
            continue

        queue_status = check_queue_status(server_address)
        if queue_status is not None:
            if queue_status['queue_running'] == [] and queue_status['queue_pending'] == []:
                print("Queue is empty, all tasks are done", flush=True)
                break

    return

def check_queue_status(server_address):
    try:
        req = urllib.request.Request(f"http://{server_address}/queue")
        response = urllib.request.urlopen(req)
        queue_info = json.loads(response.read())
        return queue_info
    except Exception as e:
        print(f"Failed to check queue status: {e}", flush=True)
        return None


def queue_prompt(prompt, client_id, server_address):
    print("Queuing request to comfyui")
    p = {"prompt": prompt, "client_id": client_id}
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data, headers=headers)
    print("Requesting queue prompt")
    return json.loads(urllib.request.urlopen(req).read())

