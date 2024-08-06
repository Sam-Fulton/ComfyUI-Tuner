import os

from mongo import find_workflow, get_db

class Outputs:
    def __init__(self, workflow_id, paths):
        self.workflow_id = workflow_id
        self.paths = paths

    @property
    def workflow_id(self):
        return self._workflow_id

    @workflow_id.setter
    def workflow_id(self, value):
        self._workflow_id = value
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
        workflow = find_workflow(db=db, workflow_id=self._workflow_id)
        if workflow is None:
            raise ValueError(f"Workflow ID does not exist: {self._workflow_id}")