"""
PyTorch Dataset for Signature Verification Pair Training and Evaluation.
"""

from pathlib import Path
from typing import Union, Optional, Callable, Dict, Any, List
import pandas as pd
import torch
from torch.utils.data import Dataset
from ml.preprocessing.signature_preprocessor import SignaturePreprocessor


class SignaturePairDataset(Dataset):
    """
    Loads signature image pairs from a CSV manifest for Siamese Network training or evaluation.
    Each item yields:
        image_1: Tensor of shape (1, H, W)
        image_2: Tensor of shape (1, H, W)
        label: Float tensor (1.0 for genuine pair, 0.0 for forged/dissimilar pair)
    """

    def __init__(
        self,
        pairs_source: Union[str, Path, pd.DataFrame, List[dict]],
        preprocessor: Optional[SignaturePreprocessor] = None,
        target_size: tuple = (224, 224),
        augment: bool = False,
        augmentor: Optional[Callable] = None,
        cache_in_memory: bool = False
    ):
        """
        Args:
            pairs_source: Path to pairs CSV, or a pandas DataFrame, or list of dicts.
            preprocessor: Custom preprocessor. If None, default SignaturePreprocessor is used.
            target_size: (H, W) if preprocessor is None.
            augment: If True, applies data augmentation.
            augmentor: Optional custom augmentation callable. If None and augment=True, uses default.
            cache_in_memory: If True, caches preprocessed tensors in RAM for faster multi-epoch training.
        """
        if isinstance(pairs_source, (str, Path)):
            self.df = pd.read_csv(pairs_source)
        elif isinstance(pairs_source, pd.DataFrame):
            self.df = pairs_source.copy()
        elif isinstance(pairs_source, list):
            self.df = pd.DataFrame(pairs_source)
        else:
            raise TypeError(f"Unsupported pairs_source type: {type(pairs_source)}")

        self.preprocessor = preprocessor or SignaturePreprocessor(target_size=target_size)
        self.augment = augment or (augmentor is not None)
        self.augmentor = augmentor
        self.cache_in_memory = cache_in_memory
        self.cache: Dict[str, torch.Tensor] = {}

    def __len__(self) -> int:
        return len(self.df)

    def _load_and_preprocess(self, path_str: str) -> torch.Tensor:
        if self.cache_in_memory and path_str in self.cache:
            return self.cache[path_str]

        # Use preprocessor
        tensor = self.preprocessor.preprocess(path_str, as_tensor=True)

        if self.cache_in_memory:
            self.cache[path_str] = tensor

        return tensor

    def _apply_augmentation(self, tensor: torch.Tensor) -> torch.Tensor:
        """Applies signing variations."""
        if not self.augment:
            return tensor

        if self.augmentor is not None:
            return self.augmentor(tensor)

        import random
        import cv2

        angle = random.uniform(-5.0, 5.0)
        img_np = tensor.squeeze(0).numpy()
        h, w = img_np.shape
        center = (w // 2, h // 2)
        m = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img_np, m, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        return torch.from_numpy(rotated).unsqueeze(0).float()

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        row = self.df.iloc[idx]
        img1_path = row["image_1_path"]
        img2_path = row["image_2_path"]
        label = float(row["label"])

        t1 = self._load_and_preprocess(img1_path)
        t2 = self._load_and_preprocess(img2_path)

        if self.augment:
            t1 = self._apply_augmentation(t1)
            t2 = self._apply_augmentation(t2)

        sample = {
            "image_1": t1,
            "image_2": t2,
            "label": torch.tensor(label, dtype=torch.float32),
            "pair_type": row.get("pair_type", "unknown"),
            "writer_1": int(row.get("writer_1", -1)),
            "writer_2": int(row.get("writer_2", -1))
        }
        return sample
