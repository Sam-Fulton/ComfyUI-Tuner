from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(features_image1, features_image2):
    return cosine_similarity([features_image1], [features_image2])
