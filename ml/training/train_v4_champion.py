"""
Deterministic Retraining and Freezing Pipeline for SYNAPSE v4 Champion.

Key Innovations:
- Architecture: Modified ResNet-18 (256-D Hyperspherical Unit Embedding)
- Objective: ForgeryAwareMetricLoss (margin_random=1.0, margin_skilled=1.25, skilled_multiplier=2.0, gamma=1.5)
- Augmentation: RealisticSignatureAugmentor
- Training Split: Writers 1-35 (data/pairs/train_pairs.csv)
- Calibration Split: Writers 36-45 (validation cohort)
- Test Cohort: Writers 46-55 (FROZEN & UNTOUCHED)
- Dual Threshold Calibration:
  * Single-Pair Operating Threshold
  * Customer Gallery Operating Threshold
- Exports:
  * artifacts/models/v4_champion_model.pt
  * artifacts/models/v4_champion_config.json
  * artifacts/models/v4_champion_threshold.json
  * artifacts/models/V4_CHAMPION_MANIFEST.json
"""

import sys
import os
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any
from collections import defaultdict
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


def compute_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def train_and_freeze_v4():
    seed = 42
    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.set_num_threads(4)
    device = torch.device("cpu")

    out_dir = Path("artifacts/models")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("==================================================")
    print("   SYNAPSE v4 CHAMPION DETERMINISTIC RETRAINING")
    print("==================================================")
    print(f"[*] Training Cohort        : Writers 1-35 (data/pairs/train_pairs.csv)")
    print(f"[*] Calibration Cohort     : Writers 36-45 (data/pairs/validation_pairs.csv)")
    print(f"[*] Test Cohort Status     : STRICTLY FROZEN (Writers 46-55)")
    print(f"[*] Loss Objective         : ForgeryAwareMetricLoss (margin_skilled=1.25, skilled_multiplier=2.0)")
    print(f"[*] Backbone Architecture  : Modified ResNet-18 (256-D L2 Norm)")
    print(f"[*] Seed                   : {seed}")

    train_df = pd.read_csv("data/pairs/train_pairs.csv")
    val_df = pd.read_csv("data/pairs/validation_pairs.csv")

    # Stratified balance focusing on skilled forgery rejection
    pos_df = train_df[train_df["label"] == 1]
    sk_df = train_df[train_df["pair_type"] == "skilled_forgery"]
    rnd_df = train_df[train_df["pair_type"] == "random_forgery"]

    n_pos = len(pos_df)
    n_sk = int(n_pos * 0.60)
    n_rnd = int(n_pos * 0.40)

    train_sub = pd.concat([
        pos_df,
        sk_df.sample(n=n_sk, replace=True, random_state=seed),
        rnd_df.sample(n=n_rnd, replace=False, random_state=seed)
    ]).sample(frac=1.0, random_state=seed).reset_index(drop=True)

    preprocessor = SignaturePreprocessor(binarization_method="otsu", target_size=(224, 224))
    augmentor = RealisticSignatureAugmentor()

    train_ds = SignaturePairDataset(train_sub, preprocessor=preprocessor, cache_in_memory=True, augment=True, augmentor=augmentor)
    val_ds = SignaturePairDataset(val_df, preprocessor=preprocessor, cache_in_memory=True, augment=False)

    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=128, shuffle=False)

    model = SiameseResNet18(embedding_dim=256, in_channels=1).to(device)
    criterion = ForgeryAwareMetricLoss(margin_random=1.0, margin_skilled=1.25, skilled_multiplier=2.0, gamma=1.5).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-4, weight_decay=1e-4)

    # 4 Epochs deterministic training
    epochs = 4
    t0 = time.time()
    for ep in range(1, epochs + 1):
        t_ep = time.time()
        model.train()
        total_loss = 0.0
        n_batches = 0
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
            total_loss += loss.item()
            n_batches += 1

        avg_loss = total_loss / max(1, n_batches)
        print(f"  --> Epoch [{ep}/{epochs}] ({time.time()-t_ep:.1f}s) | Train Loss: {avg_loss:.4f}")

    training_time = time.time() - t0

    # 1. Validation Calibration: Single-Pair
    model.eval()
    val_sims, val_labels, val_types = [], [], []
    with torch.no_grad():
        for b in val_loader:
            e1, e2 = model(b["image_1"].to(device), b["image_2"].to(device))
            dist = model.compute_distance(e1, e2)
            sim = model.compute_similarity(dist)
            val_sims.extend(sim.cpu().numpy().tolist())
            val_labels.extend(b["label"].cpu().numpy().tolist())
            val_types.extend(b["pair_type"])

    y_val = np.array(val_labels)
    s_val = np.array(val_sims)
    t_val = np.array(val_types)

    single_m = calculate_biometric_metrics(val_labels, val_sims)
    single_thresh = round(float(single_m["eer_threshold"]), 4)
    single_preds = (s_val >= single_thresh).astype(int)

    single_val_metrics = {
        "calibrated_threshold": single_thresh,
        "auc_roc": round(float(single_m["auc_roc"]), 4),
        "eer": round(float(single_m["eer"]), 4),
        "tar": round(float((single_preds[t_val == "genuine_genuine"] == 1).mean()), 4),
        "frr": round(float((single_preds[t_val == "genuine_genuine"] == 0).mean()), 4),
        "skilled_far": round(float((single_preds[t_val == "skilled_forgery"] == 1).mean()), 4),
        "random_far": round(float((single_preds[t_val == "random_forgery"] == 1).mean()), 4),
        "overall_far": round(float((single_preds[y_val == 0] == 1).mean()), 4)
    }

    # 2. Validation Calibration: Customer Gallery (3 specimens)
    gen_by_w = defaultdict(list)
    forg_by_w = defaultdict(list)
    for p in Path("data/processed").glob("*/*/*.png"):
        w_id = int(p.stem.split("_")[1])
        if 36 <= w_id <= 45:
            if "genuine" in str(p):
                gen_by_w[w_id].append(p)
            elif "forged" in str(p):
                forg_by_w[w_id].append(p)

    evaluator = CustomerGalleryEvaluator(model, device=device, gallery_size=3)
    val_writers = sorted(list(gen_by_w.keys()))
    gallery_val_res = evaluator.evaluate_cohort(val_writers, gen_by_w, forg_by_w, strategy="max")
    gallery_thresh = round(float(gallery_val_res["eer_threshold"]), 4)

    print("\n--------------------------------------------------")
    print("   DEVELOPMENT VALIDATION & DUAL CALIBRATION")
    print("--------------------------------------------------")
    print(f"[*] Single-Pair Calibrated Threshold (tau*): {single_thresh}")
    print(f"    -> AUC: {single_val_metrics['auc_roc']:.4f} | Skilled FAR: {single_val_metrics['skilled_far']*100:.2f}% | TAR: {single_val_metrics['tar']*100:.2f}%")
    print(f"[*] Gallery Calibrated Threshold (tau_gal*): {gallery_thresh}")
    print(f"    -> AUC: {gallery_val_res['roc_auc']:.4f} | Skilled FAR: {gallery_val_res['skilled_far']*100:.2f}% | TAR: {gallery_val_res['tar']*100:.2f}%")

    # Export Weights
    model_path = out_dir / "v4_champion_model.pt"
    torch.save({
        "model_state_dict": model.state_dict(),
        "model_architecture": "SiameseResNet18",
        "embedding_dim": 256,
        "calibrated_single_threshold": single_thresh,
        "calibrated_gallery_threshold": gallery_thresh,
        "optimal_threshold": single_thresh,
        "training_time_sec": round(training_time, 2),
        "validation_metrics": {
            "single_pair": single_val_metrics,
            "gallery": gallery_val_res
        }
    }, model_path)
    print(f"[+] Saved v4 model weights to: {model_path}")

    # Export Config
    config = {
        "model_name": "SYNAPSE v4 Customer-Conditioned Champion",
        "model_version": "4.0.0-champion",
        "dataset": "CEDAR Offline Signature Benchmark",
        "train_writers": list(range(1, 36)),
        "validation_writers": list(range(36, 46)),
        "frozen_test_writers": list(range(46, 56)),
        "backbone": "resnet18",
        "embedding_dimension": 256,
        "loss": "ForgeryAwareMetricLoss",
        "loss_parameters": {
            "margin_random": 1.0,
            "margin_skilled": 1.25,
            "skilled_multiplier": 2.0,
            "triplet_margin": 0.35,
            "gamma": 1.5
        },
        "optimizer": "AdamW",
        "learning_rate": 5e-4,
        "batch_size": 64,
        "epochs": epochs,
        "random_seed": seed,
        "preprocessing_version": "1.0.0-otsu-crop-pad",
        "gallery_strategy": "max",
        "enrolled_specimens_count": 3,
        "single_pair_calibrated_threshold": single_thresh,
        "gallery_calibrated_threshold": gallery_thresh,
        "frozen_calibrated_threshold": single_thresh,
        "validation_metrics": {
            "single_pair": single_val_metrics,
            "gallery": gallery_val_res
        },
        "parameter_count": sum(p.numel() for p in model.parameters()),
        "model_size_mb": round(os.path.getsize(model_path) / (1024 * 1024), 2),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    config_path = out_dir / "v4_champion_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print(f"[+] Saved v4 config to: {config_path}")

    # Export Threshold JSON
    thresh_data = {
        "single_pair_threshold": single_thresh,
        "gallery_threshold": gallery_thresh,
        "frozen_threshold": single_thresh,
        "calibrated_threshold": single_thresh,
        "calibration_cohort": "CEDAR Writers 36-45",
        "calibrated_at_utc": datetime.now(timezone.utc).isoformat()
    }
    thresh_path = out_dir / "v4_champion_threshold.json"
    with open(thresh_path, "w", encoding="utf-8") as f:
        json.dump(thresh_data, f, indent=2)
    print(f"[+] Saved v4 threshold to: {thresh_path}")

    # Export Cryptographic Manifest
    manifest = {
        "manifest_version": "1.0.0",
        "model_name": "SYNAPSE v4 Customer-Conditioned Champion",
        "model_version": "4.0.0-champion",
        "creation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "cryptographic_signatures": {
            "model_weights_sha256": compute_sha256(model_path),
            "config_sha256": compute_sha256(config_path),
            "threshold_sha256": compute_sha256(thresh_path)
        },
        "single_pair_threshold": single_thresh,
        "gallery_threshold": gallery_thresh,
        "enrolled_specimens_count": 3,
        "gallery_aggregation_rule": "max",
        "protocol_integrity_attestation": "Model trained strictly on Writers 1-35. Thresholds calibrated strictly on Writers 36-45. Zero test cohort exposure."
    }
    manifest_path = out_dir / "V4_CHAMPION_MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[+] Saved v4 cryptographic manifest to: {manifest_path}")


if __name__ == "__main__":
    train_and_freeze_v4()
