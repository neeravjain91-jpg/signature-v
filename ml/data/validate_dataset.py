"""
Dataset Validation Script.

Performs rigorous integrity checks on signature image files:
- Zero-byte files
- Unreadable/corrupted files
- Unsupported formats
- Extreme dimensions & aspect ratios
- Duplicate file hashes
- Writer sample completeness (expected 24 genuine & 24 forged)

Generates data/metadata/validation_report.json.
Does NOT silently delete any files.
"""

import json
import hashlib
from pathlib import Path
from PIL import Image
import yaml


def load_config(config_path: str = "ml/data/dataset_config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_dataset():
    cfg = load_config()
    raw_dir = Path(cfg["paths"]["raw_dir"])
    metadata_dir = Path(cfg["paths"]["metadata_dir"])
    metadata_dir.mkdir(parents=True, exist_ok=True)

    val_cfg = cfg["validation"]
    str_cfg = cfg["structure"]

    gen_dir = raw_dir / str_cfg["genuine_dir_name"]
    forg_dir = raw_dir / str_cfg["forged_dir_name"]

    if not gen_dir.exists() or not forg_dir.exists():
        print(f"[-] Raw directories not found at {raw_dir}.")
        return False

    report = {
        "status": "PASS",
        "total_files_examined": 0,
        "valid_files_count": 0,
        "anomalies_detected": {
            "zero_byte_files": [],
            "unreadable_corrupt_files": [],
            "unsupported_format_files": [],
            "undersized_dimension_files": [],
            "extreme_aspect_ratio_files": [],
            "duplicate_hashes": {}
        },
        "writer_completeness": {
            "missing_writers": [],
            "incomplete_genuine": {},
            "incomplete_forged": {}
        },
        "statistics": {}
    }

    all_files = list(gen_dir.glob("*.*")) + list(forg_dir.glob("*.*"))
    report["total_files_examined"] = len(all_files)

    seen_hashes = {}
    valid_count = 0
    writer_genuine_counts = {}
    writer_forged_counts = {}

    for file_path in all_files:
        rel_str = str(file_path.relative_to(raw_dir))
        is_genuine = str_cfg["genuine_dir_name"] in file_path.parts

        # 1. Zero-byte check
        file_size = file_path.stat().st_size
        if file_size == 0 or file_size < val_cfg["min_file_size_bytes"]:
            report["anomalies_detected"]["zero_byte_files"].append({
                "path": rel_str,
                "size_bytes": file_size
            })
            continue

        # 2. Extension check
        if file_path.suffix.lower() not in val_cfg["supported_extensions"]:
            if file_path.name.lower() in ["thumbs.db", ".ds_store", "desktop.ini"] or file_path.suffix.lower() in [".db", ".ini"]:
                report["anomalies_detected"]["unsupported_format_files"].append({
                    "path": rel_str,
                    "extension": file_path.suffix,
                    "note": "OS metadata file (ignored during training)"
                })
            else:
                report["anomalies_detected"]["unsupported_format_files"].append({
                    "path": rel_str,
                    "extension": file_path.suffix,
                    "note": "Non-conforming file"
                })
            continue

        # 3. Readability & Dimensions check
        try:
            with Image.open(file_path) as img:
                img.verify()
            # Reopen for size/dimensions (verify closes image)
            with Image.open(file_path) as img:
                w, h = img.size
                format_name = img.format
        except Exception as e:
            report["anomalies_detected"]["unreadable_corrupt_files"].append({
                "path": rel_str,
                "error": str(e)
            })
            continue

        if w < val_cfg["min_width"] or h < val_cfg["min_height"]:
            report["anomalies_detected"]["undersized_dimension_files"].append({
                "path": rel_str,
                "dimensions": [w, h],
                "min_expected": [val_cfg["min_width"], val_cfg["min_height"]]
            })
            continue

        aspect_ratio = w / h if h > 0 else 0
        if aspect_ratio < val_cfg["min_aspect_ratio"] or aspect_ratio > val_cfg["max_aspect_ratio"]:
            report["anomalies_detected"]["extreme_aspect_ratio_files"].append({
                "path": rel_str,
                "aspect_ratio": round(aspect_ratio, 4)
            })
            continue

        # 4. Duplicate Hash check
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        file_hash = hasher.hexdigest()

        if file_hash in seen_hashes:
            if file_hash not in report["anomalies_detected"]["duplicate_hashes"]:
                report["anomalies_detected"]["duplicate_hashes"][file_hash] = [seen_hashes[file_hash]]
            report["anomalies_detected"]["duplicate_hashes"][file_hash].append(rel_str)
        else:
            seen_hashes[file_hash] = rel_str

        # 5. Track completeness
        name_parts = file_path.stem.split("_")
        if len(name_parts) >= 3 and name_parts[1].isdigit():
            writer_id = int(name_parts[1])
            if is_genuine:
                writer_genuine_counts[writer_id] = writer_genuine_counts.get(writer_id, 0) + 1
            else:
                writer_forged_counts[writer_id] = writer_forged_counts.get(writer_id, 0) + 1

        valid_count += 1

    report["valid_files_count"] = valid_count

    # Check writer completeness for expected writers (1 to 55)
    expected_writers = str_cfg["expected_writers"]
    expected_gen = str_cfg["expected_genuine_per_writer"]
    expected_forg = str_cfg["expected_forged_per_writer"]

    for w_id in range(1, expected_writers + 1):
        g_cnt = writer_genuine_counts.get(w_id, 0)
        f_cnt = writer_forged_counts.get(w_id, 0)
        if g_cnt == 0 and f_cnt == 0:
            report["writer_completeness"]["missing_writers"].append(w_id)
        else:
            if g_cnt != expected_gen:
                report["writer_completeness"]["incomplete_genuine"][w_id] = {
                    "found": g_cnt,
                    "expected": expected_gen
                }
            if f_cnt != expected_forg:
                report["writer_completeness"]["incomplete_forged"][w_id] = {
                    "found": f_cnt,
                    "expected": expected_forg
                }

    # Determine overall status
    critical_unsupported = [
        f for f in report["anomalies_detected"]["unsupported_format_files"]
        if "OS metadata" not in f.get("note", "")
    ]
    has_critical_issues = (
        len(report["anomalies_detected"]["zero_byte_files"]) > 0 or
        len(report["anomalies_detected"]["unreadable_corrupt_files"]) > 0 or
        len(critical_unsupported) > 0 or
        len(report["writer_completeness"]["missing_writers"]) > 0 or
        len(report["writer_completeness"]["incomplete_genuine"]) > 0 or
        len(report["writer_completeness"]["incomplete_forged"]) > 0
    )
    if has_critical_issues:
        report["status"] = "FAIL"
    elif (
        len(report["anomalies_detected"]["unsupported_format_files"]) > 0 or
        len(report["anomalies_detected"]["undersized_dimension_files"]) > 0 or
        len(report["anomalies_detected"]["extreme_aspect_ratio_files"]) > 0 or
        len(report["anomalies_detected"]["duplicate_hashes"]) > 0
    ):
        report["status"] = "PASS_WITH_WARNINGS"
    else:
        report["status"] = "PASS"

    out_file = metadata_dir / "validation_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n================ DATASET VALIDATION REPORT ================")
    print(f"Validation Status         : {report['status']}")
    print(f"Total Files Examined      : {report['total_files_examined']}")
    print(f"Valid Files Verified      : {report['valid_files_count']}")
    print(f"Zero-Byte / Under-sized   : {len(report['anomalies_detected']['zero_byte_files'])}")
    print(f"Corrupt / Unreadable      : {len(report['anomalies_detected']['unreadable_corrupt_files'])}")
    print(f"Unsupported Formats       : {len(report['anomalies_detected']['unsupported_format_files'])}")
    print(f"Extreme Aspect Ratios     : {len(report['anomalies_detected']['extreme_aspect_ratio_files'])}")
    print(f"Duplicate Hash Groups     : {len(report['anomalies_detected']['duplicate_hashes'])}")
    print(f"Missing Writers (1..55)   : {len(report['writer_completeness']['missing_writers'])}")
    print(f"Report JSON Written To    : {out_file}")
    print("===========================================================\n")
    return report["status"] != "FAIL"


if __name__ == "__main__":
    validate_dataset()
