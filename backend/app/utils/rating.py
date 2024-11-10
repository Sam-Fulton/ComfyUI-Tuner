import trueskill
from app.utils.mongo import get_db, find_run_workflow

class Rating:
    def __init__(self, workflow_id, images=None):
        self.workflow_id = workflow_id
        self.images = images if images else []

        self.validate_workflow_exists()
        self.calculate_aggregate_rating()

    @property
    def workflow_id(self):
        return self._workflow_id

    @workflow_id.setter
    def workflow_id(self, value):
        self._workflow_id = value
        self.validate_workflow_exists()

    @property
    def images(self):
        return self._images

    @images.setter
    def images(self, value):
        self._images = value
        self.calculate_aggregate_rating()

    @property
    def aggregate_rating(self):
        return self._aggregate_rating

    @property
    def confidence(self):
        return self._confidence

    def validate_workflow_exists(self):
        db = get_db()
        workflow = find_run_workflow(db=db, run_workflow_id=self.workflow_id)
        if workflow is None:
            raise ValueError(f"Workflow ID {self.workflow_id} does not exist.")

    def calculate_aggregate_rating(self):
        if not self.images:
            self._aggregate_rating = trueskill.Rating()
            self._confidence = self._aggregate_rating.sigma
        else:
            total_mu = sum([img.trueskill_rating.mu for img in self.images])
            total_sigma = sum([img.trueskill_rating.sigma for img in self.images])
            num_images = len(self.images)
            
            self._aggregate_rating = trueskill.Rating(mu=total_mu / num_images, sigma=total_sigma / num_images)
            self._confidence = self._aggregate_rating.sigma

    def add_image(self, image):
        if image not in self.images:
            self.images.append(image)
            self.calculate_aggregate_rating()

    def update_image_rating(self, image, new_rating):
        if image in self.images:
            image.update_trueskill_rating(new_rating)
            self.calculate_aggregate_rating()

    def remove_image(self, image):
        if image in self.images:
            self.images.remove(image)
            self.calculate_aggregate_rating()
