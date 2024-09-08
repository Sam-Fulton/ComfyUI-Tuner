import os

from app.utils.mongo import find_run_workflow, get_db

class Outputs:
    def __init__(self, run_workflow_id, paths):
        self.run_workflow_id = run_workflow_id
        self.paths = paths

    @property
    def run_workflow_id(self):
        return self._run_workflow_id

    @run_workflow_id.setter
    def run_workflow_id(self, value):
        self._run_workflow_id = value
        self.validate_workflow_exists()

    @property
    def paths(self):
        return self._paths

    @paths.setter
    def paths(self, value):
        self._paths = value
        self.validate_paths()

    def validate_paths(self):
        for path in self._paths:
            if not os.path.exists(path):
                raise ValueError(f"Path does not exist: {path}")

    def validate_workflow_exists(self):
        db = get_db()
        run_workflow = find_run_workflow(db=db, run_workflow_id=self._run_workflow_id)
        if run_workflow is None:
            raise ValueError(f"Run Workflow ID does not exist: {self._run_workflow_id}")