"""
Deterministic Training & Calibration Pipeline for the SIGNATURE VMAKE Final Champion Siamese Verifier.

Pipeline Architecture:
- Backbone: SiameseResNet18 (256-D Hyperspherical Unit Embedding)
- Objective: FocalHybridMetricLoss (alpha=1.0, beta=0.5, gamma=1.0, margin=1.0, triplet_margin=0.3)
- Preprocessing: Otsu Binarization with aspect-ratio preserving bounding box crop and pad
- Augmentation: RealisticSignatureAugmentor (biomechanical rotations, shear, scale, pen noise, blur)
- Training Writers: Writers 1-35 (data/pairs/train_pairs.csv)
- Calibration Writers: Writers 36-45 (data/pairs/validation_pairs.csv)
- Test Cohort: Writers 46-55 (FROZEN & UNTOUCHED)
- Output Artifacts:
  * artifacts/models/final_champion_model.pt
  * artifacts/models/final_champion_config.json
  * artifacts/models/FINAL_CHAMPION_MANIFEST.json
"""

import sys
import os
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ml.models.architectures import SiameseResNet18
from ml.models.focal_loss import FocalHybridMetricLoss
from ml.models.dataset import SignaturePairDataset
from ml.preprocessing.signature_preprocessor import SignaturePreprocessor
from ml.preprocessing.augmentations import RealisticSignatureAugmentor
from ml.evaluation.metrics import calculate_biometric_metrics
from ml.evaluation.gallery_strategies import aggregate_gallery_scores


def compute_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def train_and_freeze_final_champion(
    train_pairs_path: str = "data/pairs/train_pairs.csv",
    val_pairs_path: str = "data/pairs/validation_pairs.csv",
    output_dir: str = "artifacts/models",
    random_seed: int = 42,
    epochs: int = 4,
    batch_size: int = 64,
    lr: float = 5e-4,
    embedding_dim: int = 256
) -> Dict[str, Any]:
    torch.manual_seed(random_seed)
    np.random.seed(random_seed)
    torch.set_num_threads(4)
    device = torch.device("cpu")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("==================================================")
    print("   SIGNATURE VMAKE FINAL CHAMPION DETERMINISTIC TRAINING")
    print("==================================================")
    print(f"[*] Training Cohort        : Writers 1-35 ({train_pairs_path})")
    print(f"[*] Calibration Cohort     : Writers 36-45 ({val_pairs_path})")
    print(f"[*] Test Cohort Status     : FROZEN & UNTOUCHED (Writers 46-55)")
    print(f"[*] Backbone Architecture  : Modified ResNet-18")
    print(f"[*] Embedding Dimension    : {embedding_dim} (L2 Unit Norm)")
    print(f"[*] Objective Function     : FocalHybridMetricLoss (alpha=1.0, beta=0.5, gamma=1.0)")
    print(f"[*] Augmentation           : RealisticSignatureAugmentor")
    print(f"[*] Random Seed            : {random_seed}")

    preprocessor = SignaturePreprocessor(binarization_method="otsu", target_size=(224, 224))
    augmentor = RealisticSignatureAugmentor()

    train_df = pd.read_csv(train_pairs_path)
    val_df = pd.read_csv(val_pairs_path)

    train_dataset = SignaturePairDataset(
        train_df,
        preprocessor=preprocessor,
        cache_in_memory=True,
        augment=True,
        augmentor=augmentor
    )
    val_dataset = SignaturePairDataset(
        val_df,
        preprocessor=preprocessor,
        cache_in_memory=True,
        augment=False
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=128, shuffle=False)

    model = SiameseResNet18(embedding_dim=embedding_dim, in_channels=1).to(device)
    criterion = FocalHybridMetricLoss(alpha=1.0, beta=0.5, contrastive_margin=1.0, triplet_margin=0.3, gamma=1.0).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

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

            optimizer.zero_grad()
            e1, e2 = model(img1, img2)
            loss = criterion(e1, e2, lbl)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()
            n_batches += 1

        avg_loss = total_loss / max(1, n_batches)
        print(f"  --> Epoch [{ep}/{epochs}] ({time.time()-t_ep:.1f}s) | Train Loss: {avg_loss:.4f}")

    total_training_sec = time.time() - t0

    # Validation & Calibration
    model.eval()
    val_sims, val_labels, val_types = [], [], []
    with torch.no_grad():
        for batch in val_loader:
            img1 = batch["image_1"].to(device)
            img2 = batch["image_2"].to(device)
            e1, e2 = model(img1, img2)
            dist = model.compute_distance(e1, e2)
            sim = model.compute_similarity(dist)
            val_sims.extend(sim.cpu().numpy().tolist())
            val_labels.extend(batch["label"].cpu().numpy().tolist())
            val_types.extend(batch["pair_type"])

    y_val = np.array(val_labels)
    s_val = np.array(val_sims)
    types_val = np.array(val_types)

    metrics = calculate_biometric_metrics(val_labels, val_sims)
    calibrated_threshold = round(float(metrics["eer_threshold"]), 4)

    preds = (s_val >= calibrated_threshold).astype(int)
    val_tar = float((preds[types_val == "genuine_genuine"] == 1).mean())
    val_frr = float((preds[types_val == "genuine_genuine"] == 0).mean())
    val_sk_far = float((preds[types_val == "skilled_forgery"] == 1).mean())
    val_rnd_far = float((preds[types_val == "random_forgery"] == 1).mean())
    val_all_far = float((preds[y_val == 0] == 1).mean())
    val_auc = round(float(metrics["auc_roc"]), 4)
    val_eer = round(float(metrics["eer"]), 4)

    print("\n--------------------------------------------------")
    print("   DEVELOPMENT VALIDATION & THRESHOLD CALIBRATION")
    print("--------------------------------------------------")
    print(f"[*] Calibrated EER Threshold (tau*): {calibrated_threshold}")
    print(f"[*] Validation ROC-AUC             : {val_auc:.4f}")
    print(f"[*] Validation EER                 : {val_eer*100:.2f}%")
    print(f"[*] Validation TAR                 : {val_tar*100:.2f}%")
    print(f"[*] Validation FRR                 : {val_frr*100:.2f}%")
    print(f"[*] Validation Overall FAR         : {val_all_far*100:.2f}%")
    print(f"[*] Validation Skilled FAR         : {val_sk_far*100:.2f}%")
    print(f"[*] Validation Random FAR          : {val_rnd_far*100:.2f}%")

    # Export Checkpoint
    model_path = out_dir / "final_champion_model.pt"
    torch.save({
        "model_state_dict": model.state_dict(),
        "model_architecture": "SiameseResNet18",
        "embedding_dim": embedding_dim,
        "calibrated_threshold": calibrated_threshold,
        "preprocessor_version": "1.0.0-otsu-crop-pad",
        "training_epochs": epochs,
        "training_time_sec": round(total_training_sec, 2),
        "validation_metrics": {
            "auc_roc": val_auc,
            "eer": val_eer,
            "tar": val_tar,
            "frr": val_frr,
            "overall_far": val_all_far,
            "skilled_forgery_far": val_sk_far,
            "random_forgery_far": val_rnd_far
        }
    }, model_path)
    print(f"[+] Saved final champion weights to: {model_path}")

    # Export Config
    config_data = {
        "model_name": "SIGNATURE VMAKE Final Champion Verifier",
        "model_version": "3.0.0-final-champion",
        "dataset": "CEDAR Offline Signature Benchmark",
        "train_writers": list(range(1, 36)),
        "validation_writers": list(range(36, 46)),
        "frozen_test_writers": list(range(46, 56)),
        "backbone": "resnet18",
        "embedding_dimension": embedding_dim,
        "loss": "FocalHybridMetricLoss",
        "loss_parameters": {
            "alpha": 1.0,
            "beta": 0.5,
            "gamma": 1.0,
            "contrastive_margin": 1.0,
            "triplet_margin": 0.3
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
        "augmentation": "RealisticSignatureAugmentor",
        "frozen_calibrated_threshold": calibrated_threshold,
        "multi_reference_strategy": "max",
        "validation_metrics": {
            "auc_roc": val_auc,
            "eer": val_eer,
            "tar": val_tar,
            "frr": val_frr,
            "overall_far": val_all_far,
            "skilled_forgery_far": val_sk_far,
            "random_forgery_far": val_rnd_far
        },
        "parameter_count": sum(p.numel() for p in model.parameters()),
        "model_size_mb": round(os.path.getsize(model_path) / (1024 * 1024), 2),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    config_path = out_dir / "final_champion_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)
    print(f"[+] Saved final champion config to: {config_path}")

    # Export Cryptographic Manifest
    manifest = {
        "manifest_version": "1.0.0",
        "model_name": "SIGNATURE VMAKE Final Champion Verifier v3.0.0",
        "creation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "cryptographic_signatures": {
            "model_weights_sha256": compute_sha256(model_path),
            "config_sha256": compute_sha256(config_path),
        },
        "frozen_calibrated_threshold": calibrated_threshold,
        "calibration_cohort": "CEDAR Writers 36-45 (1,200 pairs)",
        "test_cohort": "CEDAR Writers 46-55 (1,200 pairs)",
        "protocol_integrity_attestation": "Model trained strictly on Writers 1-35. Threshold calibrated strictly on Writers 36-45. Zero test cohort exposure."
    }
    manifest_path = out_dir / "FINAL_CHAMPION_MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[+] Saved cryptographic manifest to: {manifest_path}")

    return {
        "model_path": str(model_path),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "calibrated_threshold": calibrated_threshold,
        "val_metrics": config_data["validation_metrics"]
    }


if __name__ == "__main__":
    train_and_freeze_final_champion()
