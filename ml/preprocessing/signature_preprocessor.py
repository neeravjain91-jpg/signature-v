"""
Reusable Signature Image Preprocessing Pipeline for Siamese Verification.

Transforms raw, noisy scanned signatures into standardized, normalized stroke representations:
Raw Image
-> load
-> grayscale
-> noise suppression
-> background removal & Otsu binarization
-> tight bounding box crop
-> aspect-ratio preserved resize with centering and padding
-> float32 normalization ([0.0, 1.0])
"""

from pathlib import Path
from typing import Union, Tuple, Optional
import cv2
import numpy as np
from PIL import Image
import torch


class SignaturePreprocessor:
    def __init__(
        self,
        target_size: Tuple[int, int] = (224, 224),
        denoise: bool = True,
        denoise_kernel: int = 3,
        binarize: bool = True,
        binarization_method: str = "otsu",
        invert_colors: bool = True,
        bbox_padding: int = 10,
        normalize_range: Tuple[float, float] = (0.0, 1.0)
    ):
        """
        Args:
            target_size: (height, width) of output image. Default (224, 224).
            denoise: Apply Gaussian smoothing to reduce scan grain.
            denoise_kernel: Kernel size for smoothing filter.
            binarize: Apply binarization / thresholding.
            binarization_method: Method for thresholding ('otsu', 'adaptive', 'morphology', 'none').
            invert_colors: If True, foreground strokes are 255/1.0, background is 0/0.0.
            bbox_padding: Padding around stroke bounding box in pixels.
            normalize_range: (min, max) range for float normalization.
        """
        self.target_size = target_size
        self.denoise = denoise
        self.denoise_kernel = denoise_kernel
        self.binarize = binarize
        self.binarization_method = binarization_method
        self.invert_colors = invert_colors
        self.bbox_padding = bbox_padding
        self.normalize_range = normalize_range

    def load_image(self, image_input: Union[str, Path, np.ndarray, Image.Image]) -> np.ndarray:
        """Loads image into a standard numpy array."""
        if isinstance(image_input, (str, Path)):
            path_str = str(image_input)
            if not Path(path_str).exists():
                raise FileNotFoundError(f"Signature image file not found: {path_str}")
            # Read image as grayscale or color
            img = cv2.imread(path_str, cv2.IMREAD_UNCHANGED)
            if img is None:
                # Fallback to PIL
                pil_img = Image.open(path_str)
                img = np.array(pil_img)
            return img
        elif isinstance(image_input, Image.Image):
            return np.array(image_input)
        elif isinstance(image_input, np.ndarray):
            return image_input.copy()
        else:
            raise TypeError(f"Unsupported image input type: {type(image_input)}")

    def to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Converts any 3-channel, 4-channel, or palette image to 8-bit single-channel grayscale."""
        if image.ndim == 2:
            return image
        elif image.ndim == 3:
            if image.shape[2] == 4:  # RGBA / BGRA
                # Blend with white background before converting
                alpha = image[:, :, 3] / 255.0
                bgr = image[:, :, :3]
                white_bg = np.ones_like(bgr, dtype=np.uint8) * 255
                blended = (alpha[:, :, None] * bgr + (1 - alpha[:, :, None]) * white_bg).astype(np.uint8)
                return cv2.cvtColor(blended, cv2.COLOR_BGR2GRAY)
            elif image.shape[2] == 3:  # BGR / RGB
                return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        raise ValueError(f"Unexpected image dimensions for grayscale conversion: {image.shape}")

    def remove_noise(self, image: np.ndarray) -> np.ndarray:
        """Applies Gaussian smoothing to suppress sensor/scanner grain."""
        k = self.denoise_kernel
        if k % 2 == 0:
            k += 1
        return cv2.GaussianBlur(image, (k, k), 0)

    def binarize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Binarizes or enhances image based on self.binarization_method.
        Methods:
          - 'otsu': Otsu global thresholding.
          - 'adaptive': Local Gaussian adaptive thresholding.
          - 'morphology': Morphological illumination normalization + Otsu.
          - 'none': Returns inverted grayscale without hard binarization.
        """
        if self.binarization_method == "adaptive":
            flags = cv2.THRESH_BINARY_INV if self.invert_colors else cv2.THRESH_BINARY
            return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, flags, 21, 5)
        elif self.binarization_method == "morphology":
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
            bg = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
            sub = cv2.subtract(bg, image) if self.invert_colors else cv2.subtract(image, bg)
            norm = cv2.normalize(sub, None, 0, 255, cv2.NORM_MINMAX)
            _, thresh = cv2.threshold(norm, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return thresh
        elif self.binarization_method == "none":
            return (255 - image) if self.invert_colors else image
        else:
            # Default 'otsu'
            flags = cv2.THRESH_BINARY_INV if self.invert_colors else cv2.THRESH_BINARY
            _, thresh = cv2.threshold(image, 0, 255, flags + cv2.THRESH_OTSU)
            return thresh

    def crop_bounding_box(self, binary_image: np.ndarray) -> np.ndarray:
        """
        Finds the tight bounding box of ink stroke pixels and crops with safety padding.
        """
        # Find coordinates of foreground strokes
        stroke_mask = binary_image if self.invert_colors else (255 - binary_image)
        coords = cv2.findNonZero(stroke_mask)

        if coords is None:
            # Empty signature (e.g. blank page)
            return binary_image

        x, y, w, h = cv2.boundingRect(coords)
        img_h, img_w = binary_image.shape

        x1 = max(0, x - self.bbox_padding)
        y1 = max(0, y - self.bbox_padding)
        x2 = min(img_w, x + w + self.bbox_padding)
        y2 = min(img_h, y + h + self.bbox_padding)

        cropped = binary_image[y1:y2, x1:x2]
        return cropped

    def resize_and_pad(self, image: np.ndarray) -> np.ndarray:
        """
        Scales signature preserving original aspect ratio, then centers it within target_size canvas.
        """
        target_h, target_w = self.target_size
        crop_h, crop_w = image.shape

        if crop_h == 0 or crop_w == 0:
            bg_val = 0 if self.invert_colors else 255
            return np.full((target_h, target_w), bg_val, dtype=np.uint8)

        # Usable inner dimensions with margin
        margin = 12
        max_h = max(10, target_h - 2 * margin)
        max_w = max(10, target_w - 2 * margin)

        scale = min(max_h / crop_h, max_w / crop_w)
        new_w = max(1, int(crop_w * scale))
        new_h = max(1, int(crop_h * scale))

        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Create canvas
        bg_val = 0 if self.invert_colors else 255
        canvas = np.full((target_h, target_w), bg_val, dtype=np.uint8)

        offset_y = (target_h - new_h) // 2
        offset_x = (target_w - new_w) // 2
        canvas[offset_y:offset_y + new_h, offset_x:offset_x + new_w] = resized

        return canvas

    def normalize(self, image: np.ndarray) -> np.ndarray:
        """Normalizes pixel values from [0, 255] uint8 to float32 in [min_val, max_val]."""
        min_v, max_v = self.normalize_range
        float_img = image.astype(np.float32) / 255.0
        if min_v != 0.0 or max_v != 1.0:
            float_img = float_img * (max_v - min_v) + min_v
        return float_img

    def preprocess(
        self,
        image_input: Union[str, Path, np.ndarray, Image.Image],
        as_tensor: bool = False
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Executes complete preprocessing pipeline.
        Returns:
            np.ndarray of shape (H, W) or torch.Tensor of shape (1, H, W)
        """
        # 1. Load
        img = self.load_image(image_input)

        # 2. Grayscale
        gray = self.to_grayscale(img)

        # 3. Denoise
        if self.denoise:
            cleaned = self.remove_noise(gray)
        else:
            cleaned = gray

        # 4. Binarize & Background Removal
        if self.binarize:
            processed = self.binarize_image(cleaned)
        else:
            processed = cleaned

        # 5. Crop Bounding Box
        cropped = self.crop_bounding_box(processed)

        # 6. Resize with Aspect Ratio & Padding
        resized = self.resize_and_pad(cropped)

        # 7. Normalize
        normalized = self.normalize(resized)

        if as_tensor:
            # Return shape: (1, H, W)
            tensor = torch.from_numpy(normalized).unsqueeze(0).float()
            return tensor

        return normalized

    def preprocess_and_save(
        self,
        src_path: Union[str, Path],
        dest_path: Union[str, Path]
    ) -> Path:
        """Processes an image from src_path and saves to dest_path without modifying raw image."""
        dest_p = Path(dest_path)
        dest_p.parent.mkdir(parents=True, exist_ok=True)
        # Preprocess to uint8 for saving
        img = self.load_image(src_path)
        gray = self.to_grayscale(img)
        if self.denoise:
            cleaned = self.remove_noise(gray)
        else:
            cleaned = gray
        if self.binarize:
            processed = self.binarize_image(cleaned)
        else:
            processed = cleaned
        cropped = self.crop_bounding_box(processed)
        resized = self.resize_and_pad(cropped)
        cv2.imwrite(str(dest_p), resized)
        return dest_p
