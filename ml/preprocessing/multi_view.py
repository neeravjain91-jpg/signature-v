"""
Multi-View Signature Representation Generator.

Generates complementary visual modalities for robust handwriting authentication:
1. Raw Grayscale: Preserves ink absorption, pressure gradients, and pen drag textures.
2. Otsu Binarization: Captures clean geometric stroke topology free of background noise.
3. Edge/Contour Gradient: Captures stroke perimeter curvature and micro-hesitation edges using Sobel operators.

Supports:
- single_view: Otsu binarized (1 channel) or Grayscale (1 channel)
- two_view: [Grayscale, Otsu] (2 channels)
- three_view: [Grayscale, Otsu, Edge] (3 channels)
"""

import cv2
import numpy as np
import torch
from typing import Tuple, Literal


class MultiViewSignaturePreprocessor:
    def __init__(
        self,
        mode: Literal["single_view", "two_view", "three_view"] = "three_view",
        target_size: Tuple[int, int] = (224, 224)
    ):
        self.mode = mode
        self.target_size = target_size

    def preprocess(self, image_input, as_tensor: bool = True):
        t = self(image_input)
        if as_tensor:
            return t
        return t.numpy()

    def __call__(self, image_input) -> torch.Tensor:
        """
        Converts file path, numpy array, or PIL image into a multi-view normalized tensor.
        """
        if isinstance(image_input, (str, bytes)):
            img = cv2.imread(str(image_input), cv2.IMREAD_GRAYSCALE)
        elif isinstance(image_input, np.ndarray):
            if len(image_input.shape) == 3:
                img = cv2.cvtColor(image_input, cv2.COLOR_BGR2GRAY)
            else:
                img = image_input.copy()
        elif hasattr(image_input, "convert"):  # PIL Image
            img = np.array(image_input.convert("L"))
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        if img is None:
            raise ValueError("Failed to load image for multi-view processing.")

        # 1. Grayscale view: Resize and normalize
        h, w = img.shape
        target_h, target_w = self.target_size

        # Invert if dark signature on white paper (standardize so ink is bright, background is dark)
        if img.mean() > 127:
            img_inv = cv2.bitwise_not(img)
        else:
            img_inv = img

        # Find bounding box of signature ink
        coords = cv2.findNonZero(img_inv)
        if coords is not None:
            x, y, bw, bh = cv2.boundingRect(coords)
            cropped = img_inv[y : y + bh, x : x + bw]
        else:
            cropped = img_inv

        # Aspect-ratio preserving pad & resize
        ch, cw = cropped.shape
        scale = min(target_h / max(1, ch), target_w / max(1, cw))
        nh, nw = int(ch * scale), int(cw * scale)
        resized_gray = cv2.resize(cropped, (nw, nh), interpolation=cv2.INTER_AREA)

        padded_gray = np.zeros((target_h, target_w), dtype=np.uint8)
        top = (target_h - nh) // 2
        left = (target_w - nw) // 2
        padded_gray[top : top + nh, left : left + nw] = resized_gray

        gray_norm = padded_gray.astype(np.float32) / 255.0

        # 2. Otsu Binarization view
        _, binary = cv2.threshold(padded_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        binary_norm = binary.astype(np.float32) / 255.0

        # 3. Edge / Contour view (Sobel magnitude)
        sobelx = cv2.Sobel(padded_gray, cv2.CV_32F, 1, 0, ksize=3)
        sobely = cv2.Sobel(padded_gray, cv2.CV_32F, 0, 1, ksize=3)
        edge_mag = cv2.magnitude(sobelx, sobely)
        if edge_mag.max() > 0:
            edge_norm = edge_mag / edge_mag.max()
        else:
            edge_norm = edge_mag

        if self.mode == "single_view":
            tensor = torch.from_numpy(binary_norm).unsqueeze(0)  # (1, H, W)
        elif self.mode == "two_view":
            stacked = np.stack([gray_norm, binary_norm], axis=0)  # (2, H, W)
            tensor = torch.from_numpy(stacked)
        else:  # three_view
            stacked = np.stack([gray_norm, binary_norm, edge_norm], axis=0)  # (3, H, W)
            tensor = torch.from_numpy(stacked)

        return tensor
