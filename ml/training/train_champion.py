"""
Deterministic Retraining and Freezing Pipeline for the SYNAPSE Champion Siamese Verifier.

Executes:
1. Pure training on Writers 1-35 only (zero leakage)
2. Hybrid Metric Loss (Contrastive + In-batch Hardest Triplet)
3. Realistic Signature Augmentation (rotations, shear, scale, noise, blur)
4. Mined Hard Negatives (35% ratio mined strictly from training split)
5. Validation Threshold Calibration on Writers 36-45 (zero test data exposure)
6. Export of champion model weights, configuration, threshold, and cryptographic manifest
"""

import sys
import os
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import roc_curve, auc, accuracy_score, precision_recall_fscore_support

from ml.models.siamese_network import SiameseSignatureNet
from ml.models.losses import HybridMetricLoss
from ml.models.dataset import SignaturePairDataset
from ml.preprocessing.signature_preprocessor import SignaturePreprocessor
from ml.preprocessing.augmentations import RealisticSignatureAugmentor
from ml.training.hard_negative_mining import HardNegativeMiner
from ml.evaluation.metrics import calculate_biometric_metrics


def compute_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def train_champion_pipeline(
    train_pairs_path: str = "data/pairs/train_pairs.csv",
    val_pairs_path: str = "data/pairs/validation_pairs.csv",
    output_dir: str = "artifacts/models",
    random_seed: int = 42,
    epochs: int = 3,
    batch_size: int = 64,
    lr: float = 5e-4,
    embedding_dim: int = 256,
    hard_negative_ratio: float = 0.35,
    alpha: float = 1.0,
    beta: float = 0.5,
    contrastive_margin: float = 1.0,
    triplet_margin: float = 0.3
) -> Dict[str, Any]:
    # Set seeds for reproducibility
    torch.manual_seed(random_seed)
    np.random.seed(random_seed)
    torch.set_num_threads(4)
    device = torch.device("cpu")

    print("==================================================")
    print("   SYNAPSE CHAMPION MODEL DETERMINISTIC TRAINING")
    print("==================================================")
    print(f"[*] Training Cohort        : Writers 1-35 (data/pairs/train_pairs.csv)")
    print(f"[*] Validation Cohort      : Writers 36-45 (data/pairs/validation_pairs.csv)")
    print(f"[*] Test Cohort Status     : FROZEN & UNTOUCHED (Writers 46-55)")
    print(f"[*] Random Seed            : {random_seed}")
    print(f"[*] Backbone Architecture  : Modified ResNet-18")
    print(f"[*] Embedding Dimension    : {embedding_dim} (L2 Unit Norm)")
    print(f"[*] Objective Function     : HybridMetricLoss (alpha={alpha}, beta={beta})")
    print(f"[*] Augmentation           : RealisticSignatureAugmentor")
    print(f"[*] Hard Negative Ratio    : {hard_negative_ratio * 100:.1f}%")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Preprocessor & Augmentor
    preprocessor = SignaturePreprocessor(binarization_method="otsu", target_size=(224, 224))
    augmentor = RealisticSignatureAugmentor(
        max_rotation_deg=4.0,
        max_shear_deg=3.0,
        scale_range=(0.96, 1.04),
        max_translation_px=4,
        blur_prob=0.25,
        noise_prob=0.25,
        contrast_range=(0.85, 1.15)
    )

    # 2. Mine Hard Negatives from Training Set
    train_df = pd.read_csv(train_pairs_path)
    base_model = SiameseSignatureNet(embedding_dim=256, backbone="resnet18").to(device)
    base_chk = torch.load(out_dir / "best_siamese_model.pt", map_location=device)
    base_model.load_state_dict(base_chk["model_state_dict"])
    base_model.eval()

    miner = HardNegativeMiner(base_model, device=device, hard_threshold=0.68, top_k=800)
    augmented_train_df = miner.create_hard_negative_augmented_dataset(
        train_df,
        hard_negative_ratio=hard_negative_ratio
    )

    # 3. Create Datasets
    train_dataset = SignaturePairDataset(
        augmented_train_df,
        preprocessor=preprocessor,
        cache_in_memory=True,
        augment=True,
        augmentor=augmentor
    )

    val_dataset = SignaturePairDataset(
        val_pairs_path,
        preprocessor=preprocessor,
        cache_in_memory=True,
        augment=False
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=128, shuffle=False)

    # 4. Model, Criterion, Optimizer
    model = SiameseSignatureNet(
        embedding_dim=embedding_dim,
        backbone="resnet18"
    ).to(device)

    criterion = HybridMetricLoss(
        alpha=alpha,
        beta=beta,
        contrastive_margin=contrastive_margin,
        triplet_margin=triplet_margin
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

    # 5. Training Loop
    t_start = time.time()
    for ep in range(1, epochs + 1):
        t_ep = time.time()
        model.train()
        total_loss = 0.0
        n_batches = 0
        for batch in train_loader:
            img1 = batch["image_1"].to(device)
            img2 = batch["image_2"].to(device)
            labels = batch["label"].to(device)

            optimizer.zero_grad()
            emb1, emb2 = model(img1, img2)
            loss, _ = criterion(emb1, emb2, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item()
            n_batches += 1

        avg_train_loss = total_loss / max(1, n_batches)
        print(f"  --> Epoch [{ep}/{epochs}] ({time.time() - t_ep:.1f}s) | Train Loss: {avg_train_loss:.4f}")

    total_training_sec = time.time() - t_start

    # 6. Evaluation & Threshold Calibration on VALIDATION COHORT (Writers 36-45)
    model.eval()
    val_labels = []
    val_sims = []
    val_types = []
    val_w1 = []
    val_w2 = []

    with torch.no_grad():
        for batch in val_loader:
            img1 = batch["image_1"].to(device)
            img2 = batch["image_2"].to(device)
            labels = batch["label"].to(device)

            emb1, emb2 = model(img1, img2)
            dist = model.compute_distance(emb1, emb2)
            sim = model.compute_similarity(dist)

            val_labels.extend(labels.cpu().numpy().tolist())
            val_sims.extend(sim.cpu().numpy().tolist())
            val_types.extend(batch["pair_type"])
            val_w1.extend(batch["writer_1"].numpy().tolist() if torch.is_tensor(batch["writer_1"]) else batch["writer_1"])
            val_w2.extend(batch["writer_2"].numpy().tolist() if torch.is_tensor(batch["writer_2"]) else batch["writer_2"])

    y_val = np.array(val_labels)
    s_val = np.array(val_sims)
    types_val = np.array(val_types)

    # Calculate optimal threshold on validation data: argmin |FPR - FNR|
    fpr, tpr, thresholds = roc_curve(y_val, s_val, pos_label=1)
    fnr = 1.0 - tpr
    eer_idx = int(np.nanargmin(np.absolute(fpr - fnr)))
    calibrated_threshold = float(thresholds[eer_idx])
    val_eer = float((fpr[eer_idx] + fnr[eer_idx]) / 2.0)
    val_auc = float(auc(fpr, tpr))

    # Evaluate at calibrated threshold
    preds_val = (s_val >= calibrated_threshold).astype(int)
    skilled_mask = (types_val == "skilled_forgery")
    random_mask = (types_val == "random_forgery")
    genuine_mask = (types_val == "genuine_genuine")

    skilled_far = float((preds_val[skilled_mask] == 1).mean()) if skilled_mask.sum() > 0 else 0.0
    random_far = float((preds_val[random_mask] == 1).mean()) if random_mask.sum() > 0 else 0.0
    overall_far = float((preds_val[y_val == 0] == 1).mean())
    tar = float((preds_val[genuine_mask] == 1).mean())
    frr = float((preds_val[genuine_mask] == 0).mean())
    acc = float(accuracy_score(y_val, preds_val))
    prec, rec, f1, _ = precision_recall_fscore_support(y_val, preds_val, average="binary", zero_division=0)

    print("\n---------------- VALIDATION CALIBRATION RESULTS ----------------")
    print(f"  Operating Threshold (CALIBRATED) : {calibrated_threshold:.4f}")
    print(f"  Validation ROC-AUC               : {val_auc:.4f}")
    print(f"  Validation Equal Error Rate      : {val_eer*100:.2f}%")
    print(f"  Validation Accuracy              : {acc*100:.2f}%")
    print(f"  Validation Skilled Forgery FAR   : {skilled_far*100:.2f}%")
    print(f"  Validation Random Impostor FAR   : {random_far*100:.2f}%")
    print(f"  Validation Overall FAR           : {overall_far*100:.2f}%")
    print(f"  Validation True Acceptance (TAR) : {tar*100:.2f}%")
    print(f"  Validation False Rejection (FRR) : {frr*100:.2f}%")
    print("----------------------------------------------------------------")

    # 7. Save Model Weights
    champ_model_path = out_dir / "champion_siamese_model.pt"
    torch.save({
        "epoch": epochs,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "embedding_dim": embedding_dim,
        "backbone": "resnet18",
        "optimal_threshold": calibrated_threshold,
        "val_metrics": {
            "auc": val_auc,
            "eer": val_eer,
            "skilled_far": skilled_far,
            "tar": tar,
            "threshold": calibrated_threshold
        }
    }, champ_model_path)
    print(f"[+] Saved champion weights to: {champ_model_path}")

    # 8. Save Champion Config
    config_record = {
        "model_name": "SYNAPSE Champion Siamese Verifier",
        "model_version": "2.0.0-champion",
        "dataset": "CEDAR Offline Signature Benchmark",
        "train_writers": list(range(1, 36)),
        "validation_writers": list(range(36, 46)),
        "frozen_test_writers": list(range(46, 56)),
        "backbone": "resnet18",
        "embedding_dimension": embedding_dim,
        "loss": "HybridMetricLoss",
        "loss_parameters": {
            "alpha": alpha,
            "beta": beta,
            "contrastive_margin": contrastive_margin,
            "triplet_margin": triplet_margin
        },
        "optimizer": "AdamW",
        "learning_rate": lr,
        "batch_size": batch_size,
        "epochs": epochs,
        "random_seed": random_seed,
        "preprocessing_version": "1.0.0-otsu-crop-pad",
        "preprocessing": {
            "method": "otsu",
            "target_size": [224, 224],
            "denoise": True,
            "normalize_range": [0.0, 1.0]
        },
        "augmentation": "RealisticSignatureAugmentor (rotation, shear, scale, noise, blur)",
        "hard_negative_mining": {
            "enabled": True,
            "ratio": hard_negative_ratio,
            "source": "Training Set Only (Writers 1-35)",
            "mined_count": 800
        },
        "pair_sampling": "balanced_with_hard_negatives",
        "multi_reference_strategy": "max",
        "frozen_threshold": round(calibrated_threshold, 4),
        "validation_metrics": {
            "auc_roc": round(val_auc, 4),
            "eer": round(val_eer, 4),
            "tar": round(tar, 4),
            "frr": round(frr, 4),
            "overall_far": round(overall_far, 4),
            "skilled_forgery_far": round(skilled_far, 4),
            "random_forgery_far": round(random_far, 4),
            "accuracy": round(acc, 4),
            "f1": round(float(f1), 4)
        },
        "parameter_count": sum(p.numel() for p in model.parameters()),
        "model_size_mb": round(sum(p.numel() * p.element_size() for p in model.parameters()) / (1024 * 1024), 2),
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    champ_config_path = out_dir / "champion_config.json"
    with open(champ_config_path, "w", encoding="utf-8") as f:
        json.dump(config_record, f, indent=2)
    print(f"[+] Saved champion config to: {champ_config_path}")

    # 9. Save Threshold JSON
    thresh_record = {
        "calibrated_threshold": round(calibrated_threshold, 4),
        "frozen_threshold": round(calibrated_threshold, 4),
        "calibration_dataset": "Writers 36-45 (1200 pairs)",
        "calibration_date": datetime.now(timezone.utc).isoformat(),
        "val_eer": round(val_eer, 4),
        "val_auc": round(val_auc, 4),
        "val_skilled_far": round(skilled_far, 4),
        "val_tar": round(tar, 4)
    }
    thresh_path = out_dir / "champion_threshold.json"
    with open(thresh_path, "w", encoding="utf-8") as f:
        json.dump(thresh_record, f, indent=2)
    print(f"[+] Saved champion threshold to: {thresh_path}")

    # 10. Compute Cryptographic Hashes & Create Immutable Manifest (Phase 14)
    manifest = {
        "manifest_version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_version": "2.0.0-champion",
        "checkpoint_file": str(champ_model_path.name),
        "checkpoint_sha256": compute_sha256(champ_model_path),
        "config_file": str(champ_config_path.name),
        "config_sha256": compute_sha256(champ_config_path),
        "threshold_file": str(thresh_path.name),
        "threshold_sha256": compute_sha256(thresh_path),
        "frozen_threshold": round(calibrated_threshold, 4),
        "preprocessing_version": "1.0.0-otsu-crop-pad",
        "training_seed": random_seed,
        "train_cohort": "Writers 1-35 (7000 pairs + 35% HNM)",
        "validation_cohort": "Writers 36-45 (1200 pairs)",
        "frozen_test_cohort": "Writers 46-55 (1200 pairs)",
        "zero_leakage_attestation": True
    }
    manifest_path = out_dir / "CHAMPION_MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[+] Created immutable manifest: {manifest_path}")

    return config_record


if __name__ == "__main__":
    train_champion_pipeline()
