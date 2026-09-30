"""
SIGNATURE VMAKE v4: 5-Fold Writer-Disjoint Cross-Validation Runner.

Evaluates:
1. Forgery-Aware Metric Learning (ResNet-18 + ForgeryAwareMetricLoss)
2. Single-pair verification vs. 3-Specimen Customer Gallery verification
3. Evaluates strictly on development Writers 1-45 (zero test data exposure)
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ml.models.architectures import SiameseResNet18
from ml.models.forgery_aware_loss import ForgeryAwareMetricLoss
from ml.models.dataset import SignaturePairDataset
from ml.preprocessing.signature_preprocessor import SignaturePreprocessor
from ml.preprocessing.augmentations import RealisticSignatureAugmentor
from ml.evaluation.customer_gallery_evaluator import CustomerGalleryEvaluator
from ml.evaluation.metrics import calculate_biometric_metrics

CV_DIR = Path("data/pairs/cv_folds")
OUT_JSON = Path("artifacts/cross_validation/v4_cv_benchmark_results.json")


def run_v4_fold(fold_idx: int, epochs: int = 2, batch_size: int = 64, device: torch.device = None):
    if device is None:
        device = torch.device("cpu")

    train_path = CV_DIR / f"fold_{fold_idx}_train.csv"
    val_path = CV_DIR / f"fold_{fold_idx}_val.csv"

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)

    # Stratified balance with skilled forgery emphasis
    pos_df = train_df[train_df["label"] == 1].sample(n=1200, random_state=42)
    sk_df = train_df[train_df["pair_type"] == "skilled_forgery"].sample(n=800, random_state=42)
    rnd_df = train_df[train_df["pair_type"] == "random_forgery"].sample(n=400, random_state=42)
    train_sub = pd.concat([pos_df, sk_df, rnd_df]).sample(frac=1.0, random_state=42).reset_index(drop=True)

    preprocessor = SignaturePreprocessor(binarization_method="otsu", target_size=(224, 224))
    augmentor = RealisticSignatureAugmentor()

    train_ds = SignaturePairDataset(train_sub, preprocessor=preprocessor, cache_in_memory=True, augment=True, augmentor=augmentor)
    val_ds = SignaturePairDataset(val_df, preprocessor=preprocessor, cache_in_memory=True, augment=False)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=128, shuffle=False)

    model = SiameseResNet18(embedding_dim=256, in_channels=1).to(device)
    criterion = ForgeryAwareMetricLoss(margin_random=1.0, margin_skilled=1.25, skilled_multiplier=2.0, gamma=1.5).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-4, weight_decay=1e-4)

    # Train
    model.train()
    for ep in range(epochs):
        for batch in train_loader:
            img1 = batch["image_1"].to(device)
            img2 = batch["image_2"].to(device)
            lbl = batch["label"].to(device)
            p_types = batch["pair_type"]

            optimizer.zero_grad()
            e1, e2 = model(img1, img2)
            loss = criterion(e1, e2, lbl, p_types)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

    # 1. Single-Pair Evaluation
    model.eval()
    sims, labels, pair_types = [], [], []
    with torch.no_grad():
        for b in val_loader:
            e1, e2 = model(b["image_1"].to(device), b["image_2"].to(device))
            dist = model.compute_distance(e1, e2)
            sim = model.compute_similarity(dist)
            sims.extend(sim.cpu().numpy().tolist())
            labels.extend(b["label"].cpu().numpy().tolist())
            pair_types.extend(b["pair_type"])

    y_val = np.array(labels)
    s_val = np.array(sims)
    t_val = np.array(pair_types)

    m = calculate_biometric_metrics(labels, sims)
    th = float(m["eer_threshold"])
    preds = (s_val >= th).astype(int)

    single_pair_res = {
        "eer_threshold": round(th, 4),
        "roc_auc": round(float(m["auc_roc"]), 4),
        "eer": round(float(m["eer"]), 4),
        "tar": round(float((preds[t_val == "genuine_genuine"] == 1).mean()), 4),
        "frr": round(float((preds[t_val == "genuine_genuine"] == 0).mean()), 4),
        "skilled_far": round(float((preds[t_val == "skilled_forgery"] == 1).mean()), 4),
        "random_far": round(float((preds[t_val == "random_forgery"] == 1).mean()), 4),
        "overall_far": round(float((preds[y_val == 0] == 1).mean()), 4)
    }

    # 2. Customer Gallery Evaluation on the fold's validation writers
    from collections import defaultdict
    gen_by_w = defaultdict(list)
    forg_by_w = defaultdict(list)
    val_writers = sorted(val_df["writer_1"].unique().tolist())

    for p in Path("data/processed").glob("*/*/*.png"):
        w_id = int(p.stem.split("_")[1])
        if w_id in val_writers:
            if "genuine" in str(p):
                gen_by_w[w_id].append(p)
            elif "forged" in str(p):
                forg_by_w[w_id].append(p)

    evaluator = CustomerGalleryEvaluator(model, device=device, gallery_size=3)
    gallery_res = evaluator.evaluate_cohort(val_writers, gen_by_w, forg_by_w, strategy="max")

    return {
        "fold": fold_idx,
        "single_pair": single_pair_res,
        "gallery": gallery_res
    }


def run_all_v4_cv():
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    device = torch.device("cpu")
    torch.set_num_threads(4)

    all_fold_results = []
    print("=================================================================")
    print("   SIGNATURE VMAKE v4: 5-FOLD WRITER-DISJOINT CV BENCHMARK")
    print("   (Comparing Single-Pair vs Customer Gallery across Folds)")
    print("=================================================================")

    for f in range(5):
        t0 = time.time()
        res = run_v4_fold(f, epochs=2, device=device)
        all_fold_results.append(res)
        sp = res["single_pair"]
        gal = res["gallery"]
        print(f"  Fold {f} ({time.time()-t0:.1f}s):")
        print(f"    Single-Pair -> AUC: {sp['roc_auc']:.4f} | Skilled FAR: {sp['skilled_far']*100:.2f}% | Overall FAR: {sp['overall_far']*100:.2f}% | TAR: {sp['tar']*100:.2f}%")
        print(f"    Gallery     -> AUC: {gal['roc_auc']:.4f} | Skilled FAR: {gal['skilled_far']*100:.2f}% | Overall FAR: {gal['overall_far']*100:.2f}% | TAR: {gal['tar']*100:.2f}%")

    # Aggregate
    sp_sk_far = [r["single_pair"]["skilled_far"] for r in all_fold_results]
    gal_sk_far = [r["gallery"]["skilled_far"] for r in all_fold_results]
    sp_auc = [r["single_pair"]["roc_auc"] for r in all_fold_results]
    gal_auc = [r["gallery"]["roc_auc"] for r in all_fold_results]
    sp_tar = [r["single_pair"]["tar"] for r in all_fold_results]
    gal_tar = [r["gallery"]["tar"] for r in all_fold_results]

    summary = {
        "single_pair": {
            "mean_skilled_far": round(float(np.mean(sp_sk_far)), 4),
            "std_skilled_far": round(float(np.std(sp_sk_far)), 4),
            "mean_auc": round(float(np.mean(sp_auc)), 4),
            "std_auc": round(float(np.std(sp_auc)), 4),
            "mean_tar": round(float(np.mean(sp_tar)), 4),
            "std_tar": round(float(np.std(sp_tar)), 4),
        },
        "gallery": {
            "mean_skilled_far": round(float(np.mean(gal_sk_far)), 4),
            "std_skilled_far": round(float(np.std(gal_sk_far)), 4),
            "mean_auc": round(float(np.mean(gal_auc)), 4),
            "std_auc": round(float(np.std(gal_auc)), 4),
            "mean_tar": round(float(np.mean(gal_tar)), 4),
            "std_tar": round(float(np.std(gal_tar)), 4),
        },
        "fold_details": all_fold_results
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n-----------------------------------------------------------------")
    print("   v4 5-FOLD CROSS-VALIDATION SUMMARY:")
    print(f"   Single-Pair: Skilled FAR = {summary['single_pair']['mean_skilled_far']*100:.2f}% (+/- {summary['single_pair']['std_skilled_far']*100:.2f}%) | AUC = {summary['single_pair']['mean_auc']:.4f} | TAR = {summary['single_pair']['mean_tar']*100:.2f}%")
    print(f"   Gallery    : Skilled FAR = {summary['gallery']['mean_skilled_far']*100:.2f}% (+/- {summary['gallery']['std_skilled_far']*100:.2f}%) | AUC = {summary['gallery']['mean_auc']:.4f} | TAR = {summary['gallery']['mean_tar']*100:.2f}%")
    print("-----------------------------------------------------------------")
    print(f"[+] Saved results to {OUT_JSON}")


if __name__ == "__main__":
    run_all_v4_cv()
