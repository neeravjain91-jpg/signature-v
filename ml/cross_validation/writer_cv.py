"""
Writer-Disjoint 5-Fold Cross-Validation Data Generator for Development Cohort (Writers 1-45).

Guarantees:
- Strict writer-disjointness between training and validation in each fold.
- Exact same evaluation distribution across folds: 50% genuine-genuine, 30% skilled forgery, 20% random forgery.
- Strict isolation of Test Cohort (Writers 46-55). Writers 46-55 are NEVER included in any fold.
"""

import sys
import os
import random
import itertools
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

CV_DIR = Path("data/pairs/cv_folds")


def get_development_signatures() -> Tuple[Dict[int, List[Path]], Dict[int, List[Path]]]:
    """
    Collects genuine and forged signatures for development writers 1-45.
    Excludes test writers 46-55.
    """
    proc_dir = Path("data/processed")
    gen_by_writer = defaultdict(list)
    forg_by_writer = defaultdict(list)

    for p in sorted(proc_dir.glob("*/*/*.png")):
        w_id = int(p.stem.split("_")[1])
        if w_id > 45:
            continue  # Strictly omit test writers 46-55
        if "genuine" in str(p):
            gen_by_writer[w_id].append(p)
        elif "forged" in str(p):
            forg_by_writer[w_id].append(p)

    return gen_by_writer, forg_by_writer


def generate_fold_pairs(
    writers: List[int],
    gen_by_writer: Dict[int, List[Path]],
    forg_by_writer: Dict[int, List[Path]],
    is_eval: bool = False,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generates balanced pairs for a given list of writers.
    For evaluation: 60 positive, 36 skilled negative, 24 random negative per writer (120 pairs/writer).
    For training: 100 positive, 60 skilled negative, 40 random negative per writer (200 pairs/writer).
    """
    random.seed(seed)
    p_count = 60 if is_eval else 100
    s_count = 36 if is_eval else 60
    r_count = 24 if is_eval else 40

    records = []
    for w_id in writers:
        g_list = gen_by_writer[w_id]
        f_list = forg_by_writer[w_id]

        # 1. Genuine-Genuine Positive Pairs
        all_pos = list(itertools.combinations(g_list, 2))
        random.shuffle(all_pos)
        for img1, img2 in all_pos[:p_count]:
            records.append({
                "image_1_path": str(img1).replace("\\", "/"),
                "image_2_path": str(img2).replace("\\", "/"),
                "label": 1,
                "pair_type": "genuine_genuine",
                "writer_1": w_id,
                "writer_2": w_id
            })

        # 2. Skilled Negative Pairs (genuine vs skilled forgery)
        all_sk = list(itertools.product(g_list, f_list))
        random.shuffle(all_sk)
        for img1, img2 in all_sk[:s_count]:
            records.append({
                "image_1_path": str(img1).replace("\\", "/"),
                "image_2_path": str(img2).replace("\\", "/"),
                "label": 0,
                "pair_type": "skilled_forgery",
                "writer_1": w_id,
                "writer_2": w_id
            })

        # 3. Random Negative Pairs (genuine w_id vs genuine other within same writer pool)
        other_writers = [w for w in writers if w != w_id]
        chosen_random = []
        attempts = 0
        while len(chosen_random) < r_count and attempts < r_count * 20:
            attempts += 1
            other_w = random.choice(other_writers)
            img1 = random.choice(g_list)
            img2 = random.choice(gen_by_writer[other_w])
            pair_key = (str(img1), str(img2))
            if pair_key not in chosen_random:
                chosen_random.append(pair_key)
                records.append({
                    "image_1_path": str(img1).replace("\\", "/"),
                    "image_2_path": str(img2).replace("\\", "/"),
                    "label": 0,
                    "pair_type": "random_forgery",
                    "writer_1": w_id,
                    "writer_2": other_w
                })

    df = pd.DataFrame(records)
    # Shuffle dataframe
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


def build_5fold_cv_splits(seed: int = 42) -> None:
    CV_DIR.mkdir(parents=True, exist_ok=True)
    gen_by_writer, forg_by_writer = get_development_signatures()

    all_dev_writers = sorted(list(gen_by_writer.keys()))
    assert len(all_dev_writers) == 45, f"Expected 45 dev writers, got {len(all_dev_writers)}"
    assert max(all_dev_writers) <= 45, f"Dev writers must not exceed 45! Found max {max(all_dev_writers)}"

    # 5 folds: 9 validation writers per fold
    # Fold 0: 1-9
    # Fold 1: 10-18
    # Fold 2: 19-27
    # Fold 3: 28-36
    # Fold 4: 37-45
    fold_size = 9
    folds_metadata = []

    for fold_idx in range(5):
        val_writers = all_dev_writers[fold_idx * fold_size : (fold_idx + 1) * fold_size]
        train_writers = [w for w in all_dev_writers if w not in val_writers]

        print(f"[*] Building Fold {fold_idx}: Val Writers ({len(val_writers)}) = {val_writers[0]}-{val_writers[-1]} | Train Writers ({len(train_writers)}) = {train_writers[0]}..{train_writers[-1]}")

        val_df = generate_fold_pairs(val_writers, gen_by_writer, forg_by_writer, is_eval=True, seed=seed + fold_idx)
        train_df = generate_fold_pairs(train_writers, gen_by_writer, forg_by_writer, is_eval=False, seed=seed + fold_idx)

        val_path = CV_DIR / f"fold_{fold_idx}_val.csv"
        train_path = CV_DIR / f"fold_{fold_idx}_train.csv"

        val_df.to_csv(val_path, index=False)
        train_df.to_csv(train_path, index=False)

        folds_metadata.append({
            "fold": fold_idx,
            "val_writers": val_writers,
            "train_writers": train_writers,
            "val_pairs_count": len(val_df),
            "train_pairs_count": len(train_df),
            "val_path": str(val_path).replace("\\", "/"),
            "train_path": str(train_path).replace("\\", "/")
        })

    import json
    with open(CV_DIR / "cv_metadata.json", "w", encoding="utf-8") as f:
        json.dump(folds_metadata, f, indent=2)

    print(f"\n[+] Successfully generated 5 writer-disjoint folds in {CV_DIR}")


if __name__ == "__main__":
    build_5fold_cv_splits()
