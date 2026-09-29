"""
Realistic Offline Signature Augmentation Pipeline.

Simulates natural human signing biomechanics and banking scan acquisition variances:
1. Micro-rotations (+/- 4 degrees) mimicking casual check signing angles
2. Subtle translation / positional shifts (+/- 4 pixels)
3. Subtle anisotropic scale variations (0.96x - 1.04x) simulating pen height differences
4. Slight affine shear (+/- 3 degrees) reflecting hand slant variability
5. Mild Gaussian blur (kernel 3x3) simulating ink bleeding on low-grade paper
6. Scanner noise / salt-and-pepper grain simulating optical flatbed / check scanner artifacts
7. Dynamic contrast adjustment (0.85x - 1.15x) simulating ballpoint vs gel pen ink density

CRITICAL CONSTRAINT:
Augmentation parameters are strictly constrained to preserve stroke topography,
loop junctions, and genuine writer characteristics without synthetic distortion.
"""

import random
import cv2
import numpy as np
import torch


class RealisticSignatureAugmentor:
    """
    Applies realistic biometric variations for offline signature verification.
    """

    def __init__(
        self,
        max_rotation_deg: float = 4.0,
        max_shear_deg: float = 3.0,
        scale_range: tuple = (0.96, 1.04),
        max_translation_px: int = 4,
        blur_prob: float = 0.25,
        noise_prob: float = 0.25,
        contrast_range: tuple = (0.85, 1.15)
    ):
        self.max_rotation_deg = max_rotation_deg
        self.max_shear_deg = max_shear_deg
        self.scale_range = scale_range
        self.max_translation_px = max_translation_px
        self.blur_prob = blur_prob
        self.noise_prob = noise_prob
        self.contrast_range = contrast_range

    def __call__(self, tensor: torch.Tensor) -> torch.Tensor:
        """
        Args:
            tensor: Image tensor of shape (1, H, W) or (C, H, W) normalized to [0, 1].
        Returns:
            Augmented tensor with identical shape and dtype.
        """
        is_multi_channel = (tensor.ndim == 3 and tensor.shape[0] > 1)
        if is_multi_channel:
            c, h, w = tensor.shape
            img_np = tensor.permute(1, 2, 0).numpy().copy()  # (H, W, C)
        else:
            img_np = tensor.squeeze(0).numpy().copy()  # (H, W)
            h, w = img_np.shape

        # 1. Random Affine (Rotation + Translation + Shear + Scale)
        angle = random.uniform(-self.max_rotation_deg, self.max_rotation_deg)
        shear_x = np.deg2rad(random.uniform(-self.max_shear_deg, self.max_shear_deg))
        scale = random.uniform(self.scale_range[0], self.scale_range[1])
        tx = random.uniform(-self.max_translation_px, self.max_translation_px)
        ty = random.uniform(-self.max_translation_px, self.max_translation_px)

        # Center point
        cx, cy = w / 2.0, h / 2.0

        # Construct 2x3 affine matrix: R * S + Shear + Translation
        rad = np.deg2rad(angle)
        cos_a = np.cos(rad) * scale
        sin_a = np.sin(rad) * scale

        M = np.array([
            [cos_a - np.tan(shear_x) * sin_a, -sin_a, tx + (1 - cos_a)*cx + sin_a*cy],
            [sin_a + np.tan(shear_x) * cos_a,  cos_a, ty - sin_a*cx + (1 - cos_a)*cy]
        ], dtype=np.float32)

        bg_val = 0.0
        img_np = cv2.warpAffine(img_np, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=bg_val)

        # 2. Mild Gaussian Blur (low probability)
        if random.random() < self.blur_prob:
            img_np = cv2.GaussianBlur(img_np, (3, 3), sigmaX=0.5)

        # 3. Scanner / Flatbed grain noise (low probability)
        if random.random() < self.noise_prob:
            noise_shape = (h, w, c) if is_multi_channel else (h, w)
            noise = np.random.normal(0.0, 0.02, noise_shape).astype(np.float32)
            img_np = np.clip(img_np + noise, 0.0, 1.0)

        # 4. Contrast scaling
        c_scale = random.uniform(self.contrast_range[0], self.contrast_range[1])
        img_np = np.clip(img_np * c_scale, 0.0, 1.0)

        if is_multi_channel:
            return torch.from_numpy(img_np).permute(2, 0, 1).float()
        else:
            return torch.from_numpy(img_np).unsqueeze(0).float()
