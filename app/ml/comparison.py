from ..utils.image import Image
from trueskill import quality_1vs1, rate_1vs1

class Comparison:
    def __init__(self, image1, image2):
        if not isinstance(image1, Image) or not isinstance(image2, Image):
            raise TypeError("Both image1 and image2 must be instances of the Image class")
        self.image1 = image1
        self.image2 = image2
        self.match_quality = self.compute_match_quality()

    def compute_match_quality(self):
        """Calculates the match quality between the two images."""
        return quality_1vs1(self.image1.trueskill_rating, self.image2.trueskill_rating)

    def compare(self, outcome):
        """
        Compares the two images based on the outcome.
        :param outcome: 1 if image1 wins, -1 if image2 wins, 0 if draw.
        :return: Updated TrueSkill ratings for both images.
        """
        if outcome not in [1, 0, -1]:
            raise ValueError("Outcome must be 1 (image1 wins), -1 (image2 wins), or 0 (draw)")

        if outcome == 1:
            new_rating1, new_rating2 = rate_1vs1(self.image1.trueskill_rating, self.image2.trueskill_rating)
        elif outcome == -1:
            new_rating2, new_rating1 = rate_1vs1(self.image2.trueskill_rating, self.image1.trueskill_rating)
        else:
            new_rating1, new_rating2 = rate_1vs1(self.image1.trueskill_rating, self.image2.trueskill_rating, drawn=True)

        self.image1.update_trueskill_rating(new_rating1)
        self.image2.update_trueskill_rating(new_rating2)
        
        self.image1.update_trueskill_confidence(self.match_quality)
        self.image2.update_trueskill_confidence(self.match_quality)

        return new_rating1, new_rating2
