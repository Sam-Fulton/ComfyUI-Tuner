def get_output_paths():
    ##TODO return all possible output locations, (any nodes that contain save as class or param)
    pass

def new_outputs(before_outputs, after_outputs):
    return list(set(after_outputs) - set(before_outputs))
