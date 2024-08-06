import requests
import websocket
import uuid
import json
import urllib.request

def make_comfyUI_request(run_workflow, server_address):
    try:
        ws, client_id = open_websocket_connection(server_address)
        if not ws:
            raise ConnectionError(f"Failed to connect to the WebSocket server at {server_address}")

        prompt_result = queue_prompt(run_workflow, client_id, server_address)
        ws.close()

        return prompt_result
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    except Exception as e:
        raise SystemExit(e)

def open_websocket_connection(server_address):
    client_id = str(uuid.uuid4())
    ws = websocket.WebSocket()
    try:
        ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
        return ws, client_id
    except ConnectionRefusedError:
        print(f"Failed to connect to the WebSocket server at {server_address}")
        return None, client_id

def queue_prompt(prompt, client_id, server_address):
    p = {"prompt": prompt, "client_id": client_id}
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data, headers=headers)
    print("Requesting queue prompt")
    return json.loads(urllib.request.urlopen(req).read())