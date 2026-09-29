"""
SIGNATURE VMAKE — Classical Feature Extraction for Signature Biometrics.

Extracts engineered computer-vision features from preprocessed signature images:
1. Spatial Grid Densities (8x8 partition ink density = 64 features)
2. Directional Gradient Orientation Histograms (Sobel HOG = 128 features)
3. Horizontal & Vertical Projection Profiles (32 + 32 = 64 features)
4. Morphological & Geometric Invariants (Area ratio, aspect ratio, centroid, dispersion = 8 features)

Total feature vector length: 264 numerical features per signature image.
"""

from pathlib import Path
from typing import Union
import cv2
import numpy as np
from PIL import Image

from ml.preprocessing.signature_preprocessor import SignaturePreprocessor


class ClassicalFeatureExtractor:
    """
    Extracts 264-dimensional engineered feature vectors from offline signature images.
    """

    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size
        self.preprocessor = SignaturePreprocessor(
            target_size=target_size,
            denoise=True,
            binarize=True,
            invert_colors=True,
            normalize_range=(0.0, 1.0)
        )

    def extract(self, image_input: Union[str, Path, np.ndarray, Image.Image]) -> np.ndarray:
        """
        Extracts 264-d feature vector from raw or preprocessed image.
        """
        # Preprocess to 224x224 normalized float32 array in [0.0, 1.0]
        # Inverted: 1.0 is ink stroke, 0.0 is background
        proc_img = self.preprocessor.preprocess(image_input)
        if hasattr(proc_img, "numpy"):
            proc_img = proc_img.numpy().squeeze()
        elif proc_img.ndim == 3:
            proc_img = proc_img.squeeze()

        # Ensure float32 in [0, 1]
        img = np.clip(proc_img.astype(np.float32), 0.0, 1.0)
        h, w = img.shape

        features = []

        # 1. Spatial Grid Cell Densities (8x8 = 64 features)
        grid_rows, grid_cols = 8, 8
        cell_h, cell_w = h // grid_rows, w // grid_cols
        for r in range(grid_rows):
            for c in range(grid_cols):
                cell = img[r * cell_h:(r + 1) * cell_h, c * cell_w:(c + 1) * cell_w]
                features.append(float(np.mean(cell)))

        # 2. Horizontal Projection Profile (32 bins)
        h_proj = np.sum(img, axis=1)  # shape (224,)
        # Resample or pool into 32 bins
        bin_size_h = len(h_proj) // 32
        h_binned = [float(np.mean(h_proj[i * bin_size_h:(i + 1) * bin_size_h])) for i in range(32)]
        h_sum = sum(h_binned) + 1e-7
        features.extend([val / h_sum for val in h_binned])

        # 3. Vertical Projection Profile (32 bins)
        v_proj = np.sum(img, axis=0)  # shape (224,)
        bin_size_v = len(v_proj) // 32
        v_binned = [float(np.mean(v_proj[i * bin_size_v:(i + 1) * bin_size_v])) for i in range(32)]
        v_sum = sum(v_binned) + 1e-7
        features.extend([val / v_sum for val in v_binned])

        # 4. Geometric & Morphological Statistics (8 features)
        stroke_pixels = np.where(img > 0.1)
        num_stroke_pixels = len(stroke_pixels[0])
        total_pixels = h * w
        ink_ratio = num_stroke_pixels / total_pixels

        if num_stroke_pixels > 0:
            y_coords = stroke_pixels[0]
            x_coords = stroke_pixels[1]
            cy = float(np.mean(y_coords)) / h
            cx = float(np.mean(x_coords)) / w
            std_y = float(np.std(y_coords)) / h
            std_x = float(np.std(x_coords)) / w
            min_y, max_y = np.min(y_coords), np.max(y_coords)
            min_x, max_x = np.min(x_coords), np.max(x_coords)
            bbox_h = max(1, max_y - min_y)
            bbox_w = max(1, max_x - min_x)
            aspect_ratio = bbox_w / bbox_h
            bbox_occupancy = num_stroke_pixels / (bbox_h * bbox_w)
        else:
            cy, cx, std_y, std_x, aspect_ratio, bbox_occupancy = 0.5, 0.5, 0.0, 0.0, 1.0, 0.0

        features.extend([
            ink_ratio,
            cy,
            cx,
            std_y,
            std_x,
            aspect_ratio / 5.0,  # normalized
            bbox_occupancy,
            float(num_stroke_pixels) / 10000.0
        ])

        # 5. Directional Gradient Orientation Histograms (Sobel HOG)
        # Convert to uint8 for Sobel
        img_uint8 = (img * 255).astype(np.uint8)
        grad_x = cv2.Sobel(img_uint8, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(img_uint8, cv2.CV_32F, 0, 1, ksize=3)
        mag, angle = cv2.cartToPolar(grad_x, grad_y, angleInDegrees=True)

        # 4x4 spatial blocks x 8 orientation bins = 128 features
        num_blocks = 4
        num_bins = 8
        bh, bw = h // num_blocks, w // num_blocks
        for br in range(num_blocks):
            for bc in range(num_blocks):
                block_mag = mag[br * bh:(br + 1) * bh, bc * bw:(bc + 1) * bw]
                block_angle = angle[br * bh:(br + 1) * bh, bc * bw:(bc + 1) * bw]

                hist, _ = np.histogram(
                    block_angle,
                    bins=num_bins,
                    range=(0.0, 360.0),
                    weights=block_mag
                )
                hist_norm = np.linalg.norm(hist) + 1e-7
                features.extend((hist / hist_norm).tolist())

        feat_arr = np.array(features, dtype=np.float32)
        # Normalize whole vector to unit length
        norm = np.linalg.norm(feat_arr)
        if norm > 1e-7:
            feat_arr = feat_arr / norm

        return feat_arr

    def extract_pair_difference(self, img1, img2) -> np.ndarray:
        """
        Extracts pairwise comparative features between two signatures:
        Combines absolute difference |f1 - f2| and elementwise product f1 * f2.
        """
        f1 = self.extract(img1)
        f2 = self.extract(img2)
        diff = np.abs(f1 - f2)
        prod = f1 * f2
        pair_feat = np.concatenate([diff, prod])
        return pair_feat
