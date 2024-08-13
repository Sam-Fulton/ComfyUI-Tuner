import os
from .mongo import get_db, find_run_workflow

class QualityAssessment:
    def __init__(self, run_workflow_id: str, path: str, quality_assessment: str):
        self.run_workflow_id = run_workflow_id
        self.path = path
        self.quality_assessment = quality_assessment

    @property
    def run_workflow_id(self):
        return self._run_workflow_id

    @run_workflow_id.setter
    def run_workflow_id(self, value: str):
        run_workflow = find_run_workflow(db=get_db(), run_workflow_id=value)
        if run_workflow is None:
            raise ValueError("There is no workflow that currently exists with that id")
        self._run_workflow_id = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value: str):
        if not value or not os.path.exists(value):
            raise ValueError(f"Path does not exist: {value}")
        self._path = value

    @property
    def quality_assessment(self):
        return self._quality_assessment

    @quality_assessment.setter
    def quality_assessment(self, value: str):
        if value.lower() not in ['good', 'bad']:
            raise ValueError("quality_assessment must be either 'good' or 'bad'")
        self._quality_assessment = value.lower()