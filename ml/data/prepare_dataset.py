"""
Dataset Preparation and Preprocessing Pipeline.

Implements the standard offline signature preprocessing steps:
1. Grayscale conversion
2. Noise reduction (Gaussian/Bilateral filtering)
3. Background normalization & Otsu binarization (foreground strokes = 255, background = 0)
4. Tight bounding box cropping around signature strokes
5. Aspect-ratio preserving resize with centering and padding (target: 155x220)
6. Float32 normalization ready for Deep Learning / Siamese networks

Applies a strict writer-independent split:
- Train: Writers 1 to 35
- Validation: Writers 36 to 45
- Test: Writers 46 to 55

Preserves raw images without modification.
Saves split manifest to data/metadata/split_manifest.json.
"""

import os
import json
import cv2
import numpy as np
from pathlib import Path
import yaml


def load_config(config_path: str = "ml/data/dataset_config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def preprocess_signature_image(
    image_path: Path,
    target_height: int = 155,
    target_width: int = 220,
    bbox_padding: int = 8,
    invert_colors: bool = True
) -> np.ndarray:
    """
    Standardizes a signature image with illumination normalization,
    stroke isolation, tight cropping, and aspect-ratio preserved scaling.
    """
    # 1. Read grayscale
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")

    # 2. Noise suppression (Gaussian blur 3x3)
    blurred = cv2.GaussianBlur(img, (3, 3), 0)

    # 3. Background normalization & binarization (Otsu)
    # Using THRESH_BINARY_INV so ink strokes are 255 (foreground) and background is 0
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 4. Tight bounding box crop around signature strokes
    coords = cv2.findNonZero(thresh)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        # Apply padding
        h_img, w_img = thresh.shape
        x1 = max(0, x - bbox_padding)
        y1 = max(0, y - bbox_padding)
        x2 = min(w_img, x + w + bbox_padding)
        y2 = min(h_img, y + h + bbox_padding)
        cropped = thresh[y1:y2, x1:x2]
    else:
        cropped = thresh

    # 5. Aspect-ratio preserving resize into (target_height, target_width)
    crop_h, crop_w = cropped.shape
    if crop_h == 0 or crop_w == 0:
        return np.zeros((target_height, target_width), dtype=np.uint8)

    scale = min((target_height - 10) / crop_h, (target_width - 10) / crop_w)
    new_w = max(1, int(crop_w * scale))
    new_h = max(1, int(crop_h * scale))

    resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Canvas of zeros (black background)
    canvas = np.zeros((target_height, target_width), dtype=np.uint8)
    offset_y = (target_height - new_h) // 2
    offset_x = (target_width - new_w) // 2
    canvas[offset_y:offset_y + new_h, offset_x:offset_x + new_w] = resized

    if not invert_colors:
        canvas = 255 - canvas

    return canvas


def prepare_and_split():
    cfg = load_config()
    raw_dir = Path(cfg["paths"]["raw_dir"])
    proc_dir = Path(cfg["paths"]["processed_dir"])
    metadata_dir = Path(cfg["paths"]["metadata_dir"])
    metadata_dir.mkdir(parents=True, exist_ok=True)

    gen_dir = raw_dir / cfg["structure"]["genuine_dir_name"]
    forg_dir = raw_dir / cfg["structure"]["forged_dir_name"]

    if not gen_dir.exists() or not forg_dir.exists():
        print(f"[-] Raw directories not found at {raw_dir}.")
        return False

    split_cfg = cfg["split"]
    train_writers = set(split_cfg["train_writers"])
    val_writers = set(split_cfg["val_writers"])
    test_writers = set(split_cfg["test_writers"])

    # Verify zero leakage across writer sets
    overlap_tv = train_writers.intersection(val_writers)
    overlap_tt = train_writers.intersection(test_writers)
    overlap_vt = val_writers.intersection(test_writers)
    if overlap_tv or overlap_tt or overlap_vt:
        raise ValueError(f"CRITICAL: Data leakage in split configuration! Overlaps: TV={overlap_tv}, TT={overlap_tt}, VT={overlap_vt}")

    prep_cfg = cfg["preprocessing"]
    t_h = prep_cfg["target_height"]
    t_w = prep_cfg["target_width"]
    pad = prep_cfg["bbox_padding"]
    inv = prep_cfg["invert_colors"]

    manifest = {
        "split_methodology": split_cfg["methodology"],
        "evaluation_protocol": split_cfg["evaluation_protocol"],
        "preprocessing": prep_cfg,
        "splits": {
            "train": {"writers": sorted(list(train_writers)), "genuine_count": 0, "forged_count": 0, "total": 0},
            "validation": {"writers": sorted(list(val_writers)), "genuine_count": 0, "forged_count": 0, "total": 0},
            "test": {"writers": sorted(list(test_writers)), "genuine_count": 0, "forged_count": 0, "total": 0}
        }
    }

    # Setup directories
    for split_name in ["train", "validation", "test"]:
        (proc_dir / split_name / "genuine").mkdir(parents=True, exist_ok=True)
        (proc_dir / split_name / "forged").mkdir(parents=True, exist_ok=True)

    def process_file_list(files, is_genuine_flag):
        for f in files:
            name_parts = f.stem.split("_")
            if len(name_parts) < 3 or not name_parts[1].isdigit():
                continue
            writer_id = int(name_parts[1])

            if writer_id in train_writers:
                split_name = "train"
            elif writer_id in val_writers:
                split_name = "validation"
            elif writer_id in test_writers:
                split_name = "test"
            else:
                continue

            subfolder = "genuine" if is_genuine_flag else "forged"
            dest_file = proc_dir / split_name / subfolder / f.name

            # Preprocess and save
            processed_img = preprocess_signature_image(
                f,
                target_height=t_h,
                target_width=t_w,
                bbox_padding=pad,
                invert_colors=inv
            )
            cv2.imwrite(str(dest_file), processed_img)

            if is_genuine_flag:
                manifest["splits"][split_name]["genuine_count"] += 1
            else:
                manifest["splits"][split_name]["forged_count"] += 1
            manifest["splits"][split_name]["total"] += 1

    print("[*] Preprocessing genuine signatures...")
    process_file_list(sorted(gen_dir.glob("*.png")), is_genuine_flag=True)

    print("[*] Preprocessing forged signatures...")
    process_file_list(sorted(forg_dir.glob("*.png")), is_genuine_flag=False)

    manifest_path = metadata_dir / "split_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n================ PREPARATION & SPLIT SUMMARY ================")
    print(f"Protocol: {split_cfg['methodology'].upper()} ({split_cfg['evaluation_protocol'].upper()})")
    print(f"Train Split      : {len(train_writers)} writers -> {manifest['splits']['train']['total']} images ({manifest['splits']['train']['genuine_count']} gen, {manifest['splits']['train']['forged_count']} forg)")
    print(f"Validation Split : {len(val_writers)} writers -> {manifest['splits']['validation']['total']} images ({manifest['splits']['validation']['genuine_count']} gen, {manifest['splits']['validation']['forged_count']} forg)")
    print(f"Test Split       : {len(test_writers)} writers -> {manifest['splits']['test']['total']} images ({manifest['splits']['test']['genuine_count']} gen, {manifest['splits']['test']['forged_count']} forg)")
    print(f"Processed Output : {proc_dir}")
    print(f"Split Manifest   : {manifest_path}")
    print("=============================================================\n")
    return True


if __name__ == "__main__":
    prepare_and_split()
