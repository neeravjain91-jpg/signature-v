"""
Benchmark Customer Gallery Strategies on Validation Cohort (Writers 36-45).

Compares:
A. max similarity
B. top_k_mean (k=2)
C. median similarity
D. centroid similarity
E. variance_normalized z-score
F. customer_conditioned similarity score
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ml.models.architectures import SiameseResNet18
from ml.evaluation.customer_gallery_evaluator import CustomerGalleryEvaluator

MODEL_PATH = Path("artifacts/models/final_champion_model.pt")


def benchmark_strategies():
    device = torch.device("cpu")
    chk = torch.load(MODEL_PATH, map_location=device)
    model = SiameseResNet18(embedding_dim=256, in_channels=1).to(device)
    model.load_state_dict(chk["model_state_dict"])
    model.eval()

    evaluator = CustomerGalleryEvaluator(model, device=device, gallery_size=3)

    # Collect signatures for validation cohort (Writers 36-45)
    gen_by_writer = defaultdict(list)
    forg_by_writer = defaultdict(list)
    for p in Path("data/processed").glob("*/*/*.png"):
        w = int(p.stem.split("_")[1])
        if 36 <= w <= 45:
            if "genuine" in str(p):
                gen_by_writer[w].append(p)
            elif "forged" in str(p):
                forg_by_writer[w].append(p)

    val_writers = sorted(list(gen_by_writer.keys()))
    print(f"[*] Benchmarking gallery strategies on {len(val_writers)} validation writers ({val_writers[0]}-{val_writers[-1]})...")

    strategies = ["max", "top_k_mean", "median", "centroid", "variance_normalized", "customer_conditioned"]
    results = []

    for strat in strategies:
        res = evaluator.evaluate_cohort(val_writers, gen_by_writer, forg_by_writer, strategy=strat)
        results.append(res)
        print(f"  [{strat:22s}] -> AUC: {res['roc_auc']:.4f} | EER: {res['eer']*100:.2f}% | Skilled FAR: {res['skilled_far']*100:.2f}% | Random FAR: {res['random_far']*100:.2f}% | TAR: {res['tar']*100:.2f}%")

    out_path = Path("artifacts/evaluation/gallery_validation_strategy_benchmark.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n[+] Saved validation strategy benchmark to: {out_path}")


if __name__ == "__main__":
    benchmark_strategies()
