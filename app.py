import flask
import argparse
import os
from routes import register_blueprints

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--host', default=os.getenv('HOST', '0.0.0.0'), type=str, help='Host address to run the Tuner app on')
    parser.add_argument('-p', '--port', default=int(os.getenv('PORT', 8188)), type=int, help='Port to run the Tuner app on')
    parser.add_argument('-s', '--comfyui-address', default=os.getenv('COMFYUI_ADDRESS', '127.0.0.1:8188'), type=str, help='Server address of ComfyUI instance')
    return parser.parse_args()

def create_app(comfyui_address):
    app = flask.Flask(__name__)
    
    register_blueprints(app)

    app.config['COMFYUI_ADDRESS'] = comfyui_address

    return app
    
def main():
    args = parse_args()
    app = create_app(args.comfyui_address)
    app.run(host=args.host, port=args.port)

if __name__ == '__main__':
    main()
