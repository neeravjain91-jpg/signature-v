"""
Forensic Error Analysis Script for Final Champion Siamese Verifier.

Directly runs forward inference across the frozen 1,200 test pairs (Writers 46-55),
computes per-writer performance at the frozen operating threshold (tau* = 0.7060),
and identifies error concentration across handwriting styles.
"""

import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ml.models.architectures import SiameseResNet18
from ml.models.dataset import SignaturePairDataset
from ml.preprocessing.signature_preprocessor import SignaturePreprocessor

MODEL_PATH = Path("artifacts/models/final_champion_model.pt")
TEST_PAIRS_PATH = Path("data/pairs/test_pairs.csv")
OUT_CSV = Path("docs/FINAL_CHAMPION_WRITER_ANALYSIS.csv")
THRESH = 0.7060


def run_deep_error_analysis():
    device = torch.device("cpu")
    chk = torch.load(MODEL_PATH, map_location=device)
    model = SiameseResNet18(embedding_dim=256, in_channels=1).to(device)
    model.load_state_dict(chk["model_state_dict"])
    model.eval()

    preproc = SignaturePreprocessor(binarization_method="otsu", target_size=(224, 224))
    test_df = pd.read_csv(TEST_PAIRS_PATH)
    test_ds = SignaturePairDataset(test_df, preprocessor=preproc, cache_in_memory=True, augment=False)
    test_loader = DataLoader(test_ds, batch_size=128, shuffle=False)

    sims = []
    with torch.no_grad():
        for b in test_loader:
            e1, e2 = model(b["image_1"].to(device), b["image_2"].to(device))
            dist = model.compute_distance(e1, e2)
            sim = model.compute_similarity(dist)
            sims.extend(sim.cpu().numpy().tolist())

    eval_df = test_df.copy()
    eval_df["sim"] = sims
    eval_df["pred"] = (eval_df["sim"] >= THRESH).astype(int)

    rows = []
    for w in sorted(eval_df["writer_1"].unique()):
        sub = eval_df[eval_df["writer_1"] == w]
        gen = sub[sub["pair_type"] == "genuine_genuine"]
        sk = sub[sub["pair_type"] == "skilled_forgery"]
        rnd = sub[sub["pair_type"] == "random_forgery"]

        tar = float((gen["pred"] == 1).mean()) if len(gen) else 0.0
        frr = float((gen["pred"] == 0).mean()) if len(gen) else 0.0
        sk_far = float((sk["pred"] == 1).mean()) if len(sk) else 0.0
        rnd_far = float((rnd["pred"] == 1).mean()) if len(rnd) else 0.0
        overall_far = float((sub[sub["label"] == 0]["pred"] == 1).mean())

        gen_sim_mean = float(gen["sim"].mean()) if len(gen) else 0.0
        sk_sim_mean = float(sk["sim"].mean()) if len(sk) else 0.0
        rnd_sim_mean = float(rnd["sim"].mean()) if len(rnd) else 0.0

        rows.append({
            "writer_id": w,
            "genuine_count": len(gen),
            "skilled_count": len(sk),
            "random_count": len(rnd),
            "tar_pct": round(tar * 100, 2),
            "frr_pct": round(frr * 100, 2),
            "skilled_far_pct": round(sk_far * 100, 2),
            "random_far_pct": round(rnd_far * 100, 2),
            "overall_far_pct": round(overall_far * 100, 2),
            "mean_gen_sim": round(gen_sim_mean, 4),
            "mean_skilled_sim": round(sk_sim_mean, 4),
            "mean_random_sim": round(rnd_sim_mean, 4),
            "separation_margin": round(gen_sim_mean - sk_sim_mean, 4)
        })

    res_df = pd.DataFrame(rows)
    res_df.to_csv(OUT_CSV, index=False)
    print(f"[+] Saved writer analysis to {OUT_CSV}")
    print(res_df.to_string(index=False))


if __name__ == "__main__":
    run_deep_error_analysis()
