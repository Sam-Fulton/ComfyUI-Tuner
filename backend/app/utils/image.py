from app.utils.mongo import find_base_workflow, get_db
import os
import trueskill

class Image:
    def __init__(self, path, base_workflow_id, trueskill_rating=None, sigma=None):
        self.path = path
        self.base_workflow_id = base_workflow_id
        self.trueskill_rating = trueskill_rating if trueskill_rating else trueskill.Rating()
        self.sigma = sigma if sigma else self.trueskill_rating.sigma

        self.validate_path()
        self.validate_base_workflow_id_exists()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        self.validate_path()

    @property
    def base_workflow_id(self):
        return self._base_workflow_id

    @base_workflow_id.setter
    def base_workflow_id(self, value):
        self._base_workflow_id = value
        self.validate_base_workflow_id_exists()

    @property
    def trueskill_rating(self):
        return self._trueskill_rating

    @trueskill_rating.setter
    def trueskill_rating(self, value):
        self._trueskill_rating = value
        self.sigma = value.sigma

    def validate_path(self):
        if not os.path.exists(self._path):
            raise ValueError(f"Image path does not exist: {self._path}")

    def validate_base_workflow_id_exists(self):
        db = get_db()
        base_workflow = find_base_workflow(db=db, base_workflow_id=self._base_workflow_id)
        if base_workflow is None:
            raise ValueError(f"Base Workflow ID does not exist: {self._base_workflow_id}")

    def update_trueskill_rating(self, new_rating):
        if not isinstance(new_rating, trueskill.Rating):
            raise TypeError("new_rating must be a trueskill.Rating object")
        self.trueskill_rating = new_rating

    def update_trueskill_confidence(self, match_quality):
        self.sigma = self.trueskill_rating.sigma * match_quality
