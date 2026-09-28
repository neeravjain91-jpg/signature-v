"""
Dataset Inspection Script.

Scans the raw dataset, extracts per-image technical metadata, verifies naming conventions,
and writes an inventory report to data/metadata/dataset_inventory.csv.
"""

import os
import re
import csv
import hashlib
from pathlib import Path
from PIL import Image
import yaml


def load_config(config_path: str = "ml/data/dataset_config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def inspect_signatures():
    cfg = load_config()
    raw_dir = Path(cfg["paths"]["raw_dir"])
    metadata_dir = Path(cfg["paths"]["metadata_dir"])
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    genuine_dir = raw_dir / cfg["structure"]["genuine_dir_name"]
    forged_dir = raw_dir / cfg["structure"]["forged_dir_name"]

    if not genuine_dir.exists() or not forged_dir.exists():
        print(f"[-] Error: Raw directories not found at {raw_dir}")
        print("    Please run `python ml/data/download_dataset.py` first.")
        return False

    gen_regex = re.compile(cfg["structure"]["genuine_filename_regex"])
    forg_regex = re.compile(cfg["structure"]["forged_filename_regex"])

    records = []
    writers_found = set()
    genuine_count = 0
    forged_count = 0
    non_conforming = []

    print("[*] Inspecting genuine signatures in:", genuine_dir)
    for p in sorted(genuine_dir.glob("*.*")):
        match = gen_regex.match(p.name)
        if match:
            writer_id = int(match.group(1))
            sample_id = int(match.group(2))
            writers_found.add(writer_id)
            genuine_count += 1
            sig_type = "genuine"
        else:
            non_conforming.append(str(p))
            continue

        try:
            with Image.open(p) as img:
                width, height = img.size
                mode = img.mode
                format_name = img.format
        except Exception as e:
            width, height, mode, format_name = 0, 0, "CORRUPT", "CORRUPT"

        file_size = p.stat().st_size
        sha256 = calculate_sha256(p)

        records.append({
            "filename": p.name,
            "relative_path": str(p.relative_to(raw_dir.parent.parent)),
            "writer_id": writer_id,
            "sample_id": sample_id,
            "signature_type": sig_type,
            "is_genuine": 1,
            "format": format_name,
            "color_mode": mode,
            "width": width,
            "height": height,
            "aspect_ratio": round(width / height, 4) if height > 0 else 0,
            "file_size_bytes": file_size,
            "sha256": sha256
        })

    print("[*] Inspecting forged signatures in:", forged_dir)
    for p in sorted(forged_dir.glob("*.*")):
        match = forg_regex.match(p.name)
        if match:
            writer_id = int(match.group(1))
            sample_id = int(match.group(2))
            writers_found.add(writer_id)
            forged_count += 1
            sig_type = "forged"
        else:
            non_conforming.append(str(p))
            continue

        try:
            with Image.open(p) as img:
                width, height = img.size
                mode = img.mode
                format_name = img.format
        except Exception as e:
            width, height, mode, format_name = 0, 0, "CORRUPT", "CORRUPT"

        file_size = p.stat().st_size
        sha256 = calculate_sha256(p)

        records.append({
            "filename": p.name,
            "relative_path": str(p.relative_to(raw_dir.parent.parent)),
            "writer_id": writer_id,
            "sample_id": sample_id,
            "signature_type": sig_type,
            "is_genuine": 0,
            "format": format_name,
            "color_mode": mode,
            "width": width,
            "height": height,
            "aspect_ratio": round(width / height, 4) if height > 0 else 0,
            "file_size_bytes": file_size,
            "sha256": sha256
        })

    # Save to CSV
    csv_path = metadata_dir / "dataset_inventory.csv"
    if records:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)

    print("\n================ DATASET INSPECTION SUMMARY ================")
    print(f"Total Signatures Scanned : {len(records)}")
    print(f"Genuine Signatures       : {genuine_count}")
    print(f"Forged Signatures        : {forged_count}")
    print(f"Unique Writers Identified: {len(writers_found)} (IDs: {min(writers_found) if writers_found else 'N/A'} to {max(writers_found) if writers_found else 'N/A'})")
    print(f"Non-Conforming Filenames : {len(non_conforming)}")
    if records:
        widths = [r["width"] for r in records if r["width"] > 0]
        heights = [r["height"] for r in records if r["height"] > 0]
        print(f"Width Range              : [{min(widths)}, {max(widths)}] px (avg: {sum(widths)//len(widths)} px)")
        print(f"Height Range             : [{min(heights)}, {max(heights)}] px (avg: {sum(heights)//len(heights)} px)")
        formats = set(r["format"] for r in records)
        modes = set(r["color_mode"] for r in records)
        print(f"Image Formats Detected   : {formats}")
        print(f"Color Modes Detected     : {modes}")
    print(f"Metadata Report Written  : {csv_path}")
    print("============================================================\n")
    return True


if __name__ == "__main__":
    inspect_signatures()
