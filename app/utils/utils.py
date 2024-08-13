import os
from bson import ObjectId

def get_output_paths(run_workflow):
    comfyui_base_dir = "/app/ComfyUI/output"
    output_files = []

    for k in run_workflow.keys():
        node = run_workflow[k]
        inputs = node.get('inputs', {})
        class_type = node.get('class_type', '').lower()
        
        if 'save' in class_type:
            for input_key, input_value in inputs.items():
                if 'filename' in input_key and isinstance(input_value, str):
                    output_path = os.path.join(comfyui_base_dir, input_value)
                    output_dir = os.path.dirname(output_path)
                    
                    if output_dir and os.path.exists(output_dir):
                        for root, _, files in os.walk(output_dir):
                            print(files, flush=True)
                            for file in files:
                                print(file, flush=True)
                                output_files.append(os.path.join(root, file))

    return output_files

def new_outputs(before_outputs, after_outputs):
    return list(set(after_outputs) - set(before_outputs))

def convert_objectid_to_str(data):
    if isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(i) for i in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data