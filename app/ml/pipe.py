import os
from feature_extraction import extract_features, load_image
from similarity import calculate_similarity
from trueskill import Rating
from app.utils.image import Image
from comparison import Comparison

class Pipe:
    def __init__(self, image_paths, base_workflow_id):
        self.images = [Image(path=image_path, base_workflow_id=base_workflow_id) for image_path in image_paths]
        self.feature_vectors = {}

    def load_images(self):
        loaded_images = []
        for img in self.images:
            if os.path.exists(img.path):
                loaded_images.append(load_image(img.path))
            else:
                raise FileNotFoundError(f"Image {img.path} not found.")
        return loaded_images

    def extract_features(self):
        for img in self.images:
            features = extract_features(img.path)
            self.feature_vectors[img.path] = features

    def get_ratings(self):
        return {img.path: img.trueskill_rating for img in self.images}

    def compare_images(self, image1_path, image2_path, rating):
        image1 = next((img for img in self.images if img.path == image1_path), None)
        image2 = next((img for img in self.images if img.path == image2_path), None)

        if not image1 or not image2:
            raise ValueError("One or both images not found in the pipeline.")
        
        comparison = Comparison(image1, image2)
        comparison.compare(rating)
        return comparison.match_quality

    def categorise_new_image(self, new_image_path):
        if not os.path.exists(new_image_path):
            raise FileNotFoundError(f"New image {new_image_path} not found.")

        new_image_features = extract_features(new_image_path)

        similarities = {}
        for img_path, features in self.feature_vectors.items():
            similarity_score = calculate_similarity(new_image_features, features)
            similarities[img_path] = similarity_score

        sorted_similarities = sorted(similarities.items(), key=lambda item: item[1], reverse=True)

        return sorted_similarities

    def auto_rate_new_image(self, new_image_path):
        categorised_images = self.categorise_new_image(new_image_path)

        top_image_path = categorised_images[0][0]
        top_image = next((img for img in self.images if img.path == top_image_path), None)

        if top_image:
            new_image = Image(path=new_image_path, base_workflow_id=top_image.base_workflow_id, trueskill_rating=Rating())
            initial_rating = top_image.trueskill_rating
            new_image.update_trueskill_rating(initial_rating)
            return new_image
        else:
            raise ValueError("Failed to rate the new image.")
