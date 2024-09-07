import torch
from torchvision import models, transforms
from PIL import Image
import numpy as np
import cv2
from skimage.feature import graycomatrix, graycoprops, hog
from skimage.io import imread

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = models.resnet50(pretrained=True)
model = torch.nn.Sequential(*list(model.children())[:-1])
model = model.to(device)
model.eval()

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def load_image(image_path):
    img = Image.open(image_path).convert('RGB')
    img_tensor = preprocess(img).unsqueeze(0).to(device)
    return img_tensor

def extract_features(image_path):
    img_tensor = load_image(image_path)
    with torch.no_grad():
        features = model(img_tensor)
    return features.flatten().cpu().numpy()

def extract_features_batch(image_paths, batch_size=8):
    model.eval()
    batch_features = []
    image_tensors = [load_image(image_path) for image_path in image_paths]

    for i in range(0, len(image_tensors), batch_size):
        batch = torch.cat(image_tensors[i:i+batch_size], dim=0)
        with torch.no_grad():
            features = model(batch)
        batch_features.extend(features.flatten(start_dim=1).cpu().numpy())

    return batch_features

def extract_color_histogram(image_path, bins=(8, 8, 8)):
    image = cv2.imread(image_path)
    hist = cv2.calcHist([image], [0, 1, 2], None, bins, [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    return hist

def extract_texture_features(image_path, distances=[5], angles=[0], levels=256, symmetric=True, normed=True):
    image = imread(image_path, as_gray=True)
    image = (image * (levels - 1)).astype('uint8')
    glcm = graycomatrix(image, distances=distances, angles=angles, levels=levels, symmetric=symmetric, normed=normed)
    
    contrast = graycoprops(glcm, 'contrast')[0, 0]
    dissimilarity = graycoprops(glcm, 'dissimilarity')[0, 0]
    homogeneity = graycoprops(glcm, 'homogeneity')[0, 0]
    energy = graycoprops(glcm, 'energy')[0, 0]
    correlation = graycoprops(glcm, 'correlation')[0, 0]

    return {
        'contrast': contrast,
        'dissimilarity': dissimilarity,
        'homogeneity': homogeneity,
        'energy': energy,
        'correlation': correlation
    }

def extract_edges(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(image, 100, 200)
    return edges

def extract_hog_features(image_path):
    image = imread(image_path, as_gray=True)
    features, hog_image = hog(image, pixels_per_cell=(8, 8), cells_per_block=(2, 2), visualize=True)
    return features

def extract_combined_features(image_path):
    deep_features = extract_features(image_path)
    color_hist = extract_color_histogram(image_path)
    texture = extract_texture_features(image_path)
    
    combined_features = np.concatenate([deep_features, color_hist, list(texture.values())])
    return combined_features

##TODO take positive and negative clip text of the workflow and check the image based on this information