import os
from mongo import get_db, find_workflow

class QualityAssessment:
    def __init__(self, workflow_id, path, quality_assessment):
        self.workflow_id = workflow_id
        self.path = path
        self.quality_assessment = quality_assessment

    @property
    def workflow_id(self):
        return self._workflow_id

    @workflow_id.setter
    def workflow_id(self, value):
        workflow = find_workflow(db=get_db(), workflow_id=value)
        if workflow is None:
            raise ValueError("There is no workflow that currently exists with that id")
        self._workflow_id = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if not value or not os.path.exists(value):
            raise ValueError(f"Path does not exist: {value}")
        self._path = value

    @property
    def quality_assessment(self):
        return self._quality_assessment

    @quality_assessment.setter
    def quality_assessment(self, value):
        if value not in ['good', 'bad']:
            raise ValueError("quality_assessment must be either 'good' or 'bad'")
        self._quality_assessment = value

