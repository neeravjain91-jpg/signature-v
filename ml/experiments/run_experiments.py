"""
Comprehensive Systematic Experimentation Suite for SYNAPSE.

Executes controlled validation experiments across:
- Hard Negative Mining (Phase 4)
- Curriculum Learning (Phase 5)
- Class & Pair Balancing (Phase 6)
- Realistic Augmentation (Phase 7)
- Preprocessing Pipeline Ablation (Phase 8)
- Backbone Architectures (Phase 9)
- Embedding Dimensions (Phase 10)
- Metric Loss Functions & Hybrid Objectives (Phases 11 & 12)
- Multi-Sample Reference Aggregation (Phase 13)

CRITICAL PROTOCOL INTEGRITY:
- All training is strictly confined to Writers 1-35.
- All evaluation, threshold calibration, and model selection strictly uses Validation cohort (Writers 36-45).
- Test set (Writers 46-55) is NEVER accessed during this suite.
- Results are recorded directly into ml/experiments/experiment_registry.json.
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from sklearn.metrics import roc_curve, auc, accuracy_score, precision_recall_fscore_support

from ml.models.siamese_network import SiameseSignatureNet
from ml.models.losses import ContrastiveLoss, TripletLoss, HybridMetricLoss
from ml.models.dataset import SignaturePairDataset
from ml.preprocessing.signature_preprocessor import SignaturePreprocessor
from ml.preprocessing.augmentations import RealisticSignatureAugmentor
from ml.training.hard_negative_mining import HardNegativeMiner
from ml.evaluation.metrics import calculate_biometric_metrics

REGISTRY_PATH = Path("ml/experiments/experiment_registry.json")


def load_registry() -> List[Dict[str, Any]]:
    if REGISTRY_PATH.exists():
        try:
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_registry_record(record: Dict[str, Any]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    registry = load_registry()
    # Replace if exp_id exists, else append
    existing_idx = next((i for i, r in enumerate(registry) if r["experiment_id"] == record["experiment_id"]), None)
    if existing_idx is not None:
        registry[existing_idx] = record
    else:
        registry.append(record)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    print(f"    [Registry] Appended/Updated {record['experiment_id']} in {REGISTRY_PATH}")


def evaluate_on_validation(
    model: SiameseSignatureNet,
    val_dataset: SignaturePairDataset,
    device: torch.device,
    batch_size: int = 128
) -> Dict[str, Any]:
    model.eval()
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    all_labels = []
    all_sims = []
    pair_types = []
    latencies = []

    with torch.no_grad():
        for batch in val_loader:
            img1 = batch["image_1"].to(device)
            img2 = batch["image_2"].to(device)
            labels = batch["label"].to(device)

            t0 = time.perf_counter()
            emb1, emb2 = model(img1, img2)
            dist = model.compute_distance(emb1, emb2)
            sim = model.compute_similarity(dist)
            t1 = time.perf_counter()

            latencies.append(((t1 - t0) / img1.shape[0]) * 1000.0)
            all_labels.extend(labels.cpu().numpy().tolist())
            all_sims.extend(sim.cpu().numpy().tolist())
            pair_types.extend(batch["pair_type"])

    y_true = np.array(all_labels)
    y_scores = np.array(all_sims)
    pair_types = np.array(pair_types)

    metrics = calculate_biometric_metrics(all_labels, all_sims)
    opt_thresh = float(metrics["eer_threshold"])
    preds = (y_scores >= opt_thresh).astype(int)

    skilled_mask = (pair_types == "skilled_forgery")
    skilled_far = float((preds[skilled_mask] == 1).mean()) if skilled_mask.sum() > 0 else 0.0

    random_mask = (pair_types == "random_forgery")
    random_far = float((preds[random_mask] == 1).mean()) if random_mask.sum() > 0 else 0.0

    genuine_mask = (pair_types == "genuine_genuine")
    tar = float((preds[genuine_mask] == 1).mean()) if genuine_mask.sum() > 0 else 0.0
    frr = float((preds[genuine_mask] == 0).mean()) if genuine_mask.sum() > 0 else 0.0

    neg_mask = (y_true == 0)
    overall_far = float((preds[neg_mask] == 1).mean()) if neg_mask.sum() > 0 else 0.0

    acc = float(accuracy_score(y_true, preds))
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, preds, average="binary", zero_division=0)
    total_params = sum(p.numel() for p in model.parameters())

    return {
        "validation_threshold": round(opt_thresh, 4),
        "validation_AUC": round(float(metrics["auc_roc"]), 4),
        "validation_FAR": round(overall_far, 4),
        "validation_FRR": round(frr, 4),
        "validation_TAR": round(tar, 4),
        "validation_EER": round(float(metrics["eer"]), 4),
        "validation_skilled_FAR": round(skilled_far, 4),
        "validation_random_FAR": round(random_far, 4),
        "validation_accuracy": round(acc, 4),
        "validation_F1": round(float(f1), 4),
        "parameter_count": total_params,
        "inference_latency_ms": round(float(np.mean(latencies)), 2)
    }


def train_and_eval_experiment(
    exp_id: str,
    backbone: str = "resnet18",
    embedding_dim: int = 256,
    loss_name: str = "contrastive",
    loss_margin: float = 1.0,
    alpha: float = 1.0,
    beta: float = 0.5,
    epochs: int = 2,
    batch_size: int = 64,
    lr: float = 5e-4,
    use_augmentation: bool = True,
    augmentor_type: str = "baseline",
    preprocessor_method: str = "otsu",
    hard_negative_ratio: float = 0.0,
    pair_balance_mode: str = "standard",
    max_train_samples: Optional[int] = 2500,
    device: torch.device = None
) -> Tuple[Dict[str, Any], SiameseSignatureNet]:
    if device is None:
        device = torch.device("cpu")

    print(f"\n=======================================================")
    print(f"[*] EXPERIMENT: {exp_id}")
    print(f"    Backbone: {backbone} | Dim: {embedding_dim} | Loss: {loss_name}")
    print(f"    Aug: {augmentor_type} | Preproc: {preprocessor_method} | HardNegRatio: {hard_negative_ratio}")
    print(f"=======================================================")

    train_df = pd.read_csv("data/pairs/train_pairs.csv")

    if pair_balance_mode == "variant_a":
        pos_df = train_df[train_df["label"] == 1]
        sk_df = train_df[train_df["pair_type"] == "skilled_forgery"]
        rnd_df = train_df[train_df["pair_type"] == "random_forgery"]
        n_pos = len(pos_df)
        n_neg_each = n_pos // 2
        sk_sample = sk_df.sample(n=n_neg_each, replace=False, random_state=42)
        rnd_sample = rnd_df.sample(n=n_neg_each, replace=True, random_state=42)
        train_df = pd.concat([pos_df, sk_sample, rnd_sample], ignore_index=True)
    elif pair_balance_mode == "variant_b":
        pos_df = train_df[train_df["label"] == 1]
        sk_df = train_df[train_df["pair_type"] == "skilled_forgery"]
        rnd_df = train_df[train_df["pair_type"] == "random_forgery"]
        n_total = len(train_df)
        n_pos = int(n_total * 0.40)
        n_sk = int(n_total * 0.40)
        n_rnd = int(n_total * 0.20)
        train_df = pd.concat([
            pos_df.sample(n=n_pos, replace=False, random_state=42),
            sk_df.sample(n=n_sk, replace=True, random_state=42),
            rnd_df.sample(n=n_rnd, replace=False, random_state=42)
        ], ignore_index=True)

    preproc = SignaturePreprocessor(binarization_method=preprocessor_method)

    if augmentor_type == "realistic":
        augmentor = RealisticSignatureAugmentor()
    elif augmentor_type == "baseline":
        augmentor = None
    else:
        augmentor = None
        use_augmentation = False

    # Hard negative mining from training set if requested
    if hard_negative_ratio > 0.0:
        base_chk = torch.load("artifacts/models/best_siamese_model.pt", map_location=device)
        mining_model = SiameseSignatureNet(embedding_dim=256, backbone="resnet18").to(device)
        mining_model.load_state_dict(base_chk["model_state_dict"])
        miner = HardNegativeMiner(mining_model, device=device, hard_threshold=0.68, top_k=800)
        train_df = miner.create_hard_negative_augmented_dataset(train_df, hard_negative_ratio=hard_negative_ratio)

    if max_train_samples and len(train_df) > max_train_samples:
        # Stratified subsample
        pos = train_df[train_df["label"] == 1].sample(n=max_train_samples//2, random_state=42)
        neg = train_df[train_df["label"] == 0].sample(n=max_train_samples//2, random_state=42)
        train_df = pd.concat([pos, neg], ignore_index=True).sample(frac=1.0, random_state=42).reset_index(drop=True)

    train_dataset = SignaturePairDataset(
        train_df,
        preprocessor=preproc,
        cache_in_memory=True,
        augment=use_augmentation,
        augmentor=augmentor
    )

    val_dataset = SignaturePairDataset(
        "data/pairs/validation_pairs.csv",
        preprocessor=preproc,
        cache_in_memory=True,
        augment=False
    )

    model = SiameseSignatureNet(
        embedding_dim=embedding_dim,
        backbone=backbone
    ).to(device)

    if loss_name == "triplet":
        criterion = TripletLoss(margin=loss_margin).to(device)
    elif loss_name == "hybrid":
        criterion = HybridMetricLoss(alpha=alpha, beta=beta, contrastive_margin=loss_margin, triplet_margin=0.3).to(device)
    else:
        criterion = ContrastiveLoss(margin=loss_margin).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=True)

    model.train()
    for ep in range(1, epochs + 1):
        t_ep_start = time.time()
        total_loss = 0.0
        n_batches = 0
        for batch in train_loader:
            img1 = batch["image_1"].to(device)
            img2 = batch["image_2"].to(device)
            labels = batch["label"].to(device)

            optimizer.zero_grad()
            emb1, emb2 = model(img1, img2)

            if loss_name == "hybrid":
                loss, _ = criterion(emb1, emb2, labels)
            else:
                loss = criterion(emb1, emb2, labels)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()
            n_batches += 1

        avg_loss = total_loss / max(1, n_batches)
        ep_sec = time.time() - t_ep_start
        print(f"    Epoch [{ep}/{epochs}] ({ep_sec:.1f}s) - Train Loss: {avg_loss:.4f}")

    val_results = evaluate_on_validation(model, val_dataset, device, batch_size=128)
    print(f"    -> Val AUC: {val_results['validation_AUC']} | EER: {val_results['validation_EER']*100:.2f}% | "
          f"Skilled FAR: {val_results['validation_skilled_FAR']*100:.2f}% | TAR: {val_results['validation_TAR']*100:.2f}%")

    param_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
    model_size_mb = round(param_bytes / (1024 * 1024), 2)

    record = {
        "experiment_id": exp_id,
        "date": datetime.now(timezone.utc).isoformat(),
        "dataset": "CEDAR Offline Signature Dataset",
        "split": "Train: W1-35, Val: W36-45",
        "seed": 42,
        "preprocessing": preprocessor_method,
        "augmentation": augmentor_type,
        "backbone": backbone,
        "pretrained_status": (backbone == "resnet18_pretrained"),
        "embedding_dimension": embedding_dim,
        "loss": loss_name,
        "margin": loss_margin,
        "optimizer": "AdamW",
        "learning_rate": lr,
        "batch_size": batch_size,
        "epochs": epochs,
        "hard_negative_mining": hard_negative_ratio > 0.0,
        "hard_negative_ratio": hard_negative_ratio,
        "pair_sampling": pair_balance_mode,
        "reference_aggregation": "pairwise_distance",
        "validation_threshold": val_results["validation_threshold"],
        "validation_AUC": val_results["validation_AUC"],
        "validation_FAR": val_results["validation_FAR"],
        "validation_FRR": val_results["validation_FRR"],
        "validation_TAR": val_results["validation_TAR"],
        "validation_EER": val_results["validation_EER"],
        "validation_skilled_FAR": val_results["validation_skilled_FAR"],
        "validation_random_FAR": val_results["validation_random_FAR"],
        "validation_accuracy": val_results["validation_accuracy"],
        "validation_F1": val_results["validation_F1"],
        "parameter_count": val_results["parameter_count"],
        "model_size_mb": model_size_mb,
        "inference_latency_ms": val_results["inference_latency_ms"]
    }

    save_registry_record(record)
    return record, model


def evaluate_multi_reference_strategies(
    model: SiameseSignatureNet,
    val_manifest_path: str = "data/pairs/validation_pairs.csv",
    num_references: int = 3,
    device: torch.device = None
) -> Dict[str, Dict[str, float]]:
    if device is None:
        device = torch.device("cpu")

    model.eval()
    preproc = SignaturePreprocessor()
    df = pd.read_csv(val_manifest_path)

    img_cache = {}
    unique_paths = set(df["image_1_path"]).union(set(df["image_2_path"]))
    for p in unique_paths:
        t = preproc.preprocess(p, as_tensor=True)
        img_cache[p] = t

    writers = sorted(df["writer_1"].unique())
    writer_refs = {}
    for w in writers:
        w_df = df[(df["writer_1"] == w) & (df["label"] == 1)]
        ref_candidates = list(w_df["image_1_path"].unique())[:num_references]
        writer_refs[w] = ref_candidates

    writer_ref_embs = {}
    with torch.no_grad():
        for w, paths in writer_refs.items():
            tensors = torch.stack([img_cache[p] for p in paths]).to(device)
            embs = model.forward_one(tensors)
            writer_ref_embs[w] = embs

    strategies = ["max", "mean", "top_k", "centroid", "median"]
    strat_scores = {s: [] for s in strategies}
    strat_labels = []
    strat_types = []

    with torch.no_grad():
        for idx, row in df.iterrows():
            w = row["writer_1"]
            if w not in writer_ref_embs:
                continue
            ref_embs = writer_ref_embs[w]
            q_tensor = img_cache[row["image_2_path"]].unsqueeze(0).to(device)
            q_emb = model.forward_one(q_tensor)

            dists = torch.norm(ref_embs - q_emb, p=2, dim=1)
            sims = torch.clamp(1.0 - (dists / 2.0), 0.0, 1.0).cpu().numpy()

            strat_scores["max"].append(float(np.max(sims)))
            strat_scores["mean"].append(float(np.mean(sims)))
            k = min(2, len(sims))
            strat_scores["top_k"].append(float(np.mean(np.partition(sims, -k)[-k:])))
            centroid_emb = F.normalize(torch.mean(ref_embs, dim=0, keepdim=True), p=2, dim=1)
            dist_c = torch.norm(centroid_emb - q_emb, p=2, dim=1)
            strat_scores["centroid"].append(float(torch.clamp(1.0 - (dist_c / 2.0), 0.0, 1.0).item()))
            strat_scores["median"].append(float(np.median(sims)))

            strat_labels.append(int(row["label"]))
            strat_types.append(row["pair_type"])

    y_true = np.array(strat_labels)
    strat_types = np.array(strat_types)
    skilled_mask = (strat_types == "skilled_forgery")

    results = {}
    for s in strategies:
        scores = np.array(strat_scores[s])
        fpr, tpr, thresholds = roc_curve(y_true, scores)
        roc_auc = float(auc(fpr, tpr))
        fnr = 1 - tpr
        eer_idx = int(np.nanargmin(np.absolute(fnr - fpr)))
        eer = float(fpr[eer_idx])
        opt_thresh = float(thresholds[eer_idx])

        preds = (scores >= opt_thresh).astype(int)
        skilled_far = float((preds[skilled_mask] == 1).mean()) if skilled_mask.sum() > 0 else 0.0
        tar = float((preds[y_true == 1] == 1).mean())
        far = float((preds[y_true == 0] == 1).mean())

        results[s] = {
            "strategy": s,
            "roc_auc": round(roc_auc, 4),
            "eer": round(eer, 4),
            "threshold": round(opt_thresh, 4),
            "skilled_far": round(skilled_far, 4),
            "tar": round(tar, 4),
            "overall_far": round(far, 4)
        }

    return results


def run_all_experiments():
    torch.set_num_threads(4)
    device = torch.device("cpu")

    # EXP-001 Baseline Replica
    rec1, model_base = train_and_eval_experiment(
        exp_id="EXP-001-BASELINE",
        backbone="resnet18",
        embedding_dim=256,
        loss_name="contrastive",
        loss_margin=1.0,
        epochs=2,
        augmentor_type="baseline",
        preprocessor_method="otsu",
        hard_negative_ratio=0.0,
        pair_balance_mode="standard",
        device=device
    )

    # EXP-002 Hard Negative Mining
    rec2, _ = train_and_eval_experiment(
        exp_id="EXP-002-HARD-MINING",
        backbone="resnet18",
        embedding_dim=256,
        loss_name="contrastive",
        loss_margin=1.0,
        epochs=2,
        augmentor_type="baseline",
        preprocessor_method="otsu",
        hard_negative_ratio=0.35,
        pair_balance_mode="standard",
        device=device
    )

    # EXP-003 Pair Balancing A (50/25/25)
    rec3, _ = train_and_eval_experiment(
        exp_id="EXP-003-PAIR-BALANCE-A",
        backbone="resnet18",
        embedding_dim=256,
        loss_name="contrastive",
        loss_margin=1.0,
        epochs=2,
        augmentor_type="baseline",
        preprocessor_method="otsu",
        pair_balance_mode="variant_a",
        device=device
    )

    # EXP-004 Pair Balancing B (40/40/20)
    rec4, _ = train_and_eval_experiment(
        exp_id="EXP-004-PAIR-BALANCE-B",
        backbone="resnet18",
        embedding_dim=256,
        loss_name="contrastive",
        loss_margin=1.0,
        epochs=2,
        augmentor_type="baseline",
        preprocessor_method="otsu",
        pair_balance_mode="variant_b",
        device=device
    )

    # EXP-005 Realistic Augmentation
    rec5, _ = train_and_eval_experiment(
        exp_id="EXP-005-REALISTIC-AUG",
        backbone="resnet18",
        embedding_dim=256,
        loss_name="contrastive",
        loss_margin=1.0,
        epochs=2,
        augmentor_type="realistic",
        preprocessor_method="otsu",
        device=device
    )

    # EXP-006 Adaptive Gaussian Preproc
    rec6, _ = train_and_eval_experiment(
        exp_id="EXP-006-PREPROC-ADAPTIVE",
        backbone="resnet18",
        embedding_dim=256,
        loss_name="contrastive",
        loss_margin=1.0,
        epochs=2,
        augmentor_type="baseline",
        preprocessor_method="adaptive",
        device=device
    )

    # EXP-007 Morphological Preproc
    rec7, _ = train_and_eval_experiment(
        exp_id="EXP-007-PREPROC-MORPHOLOGY",
        backbone="resnet18",
        embedding_dim=256,
        loss_name="contrastive",
        loss_margin=1.0,
        epochs=2,
        augmentor_type="baseline",
        preprocessor_method="morphology",
        device=device
    )

    # EXP-008 Custom CNN Backbone
    rec8, _ = train_and_eval_experiment(
        exp_id="EXP-008-BACKBONE-CUSTOM-CNN",
        backbone="custom_cnn",
        embedding_dim=256,
        loss_name="contrastive",
        loss_margin=1.0,
        epochs=2,
        augmentor_type="baseline",
        preprocessor_method="otsu",
        device=device
    )

    # EXP-009 Embedding Dimension 128
    rec9, _ = train_and_eval_experiment(
        exp_id="EXP-009-EMB-DIM-128",
        backbone="resnet18",
        embedding_dim=128,
        loss_name="contrastive",
        loss_margin=1.0,
        epochs=2,
        augmentor_type="baseline",
        preprocessor_method="otsu",
        device=device
    )

    # EXP-010 Embedding Dimension 512
    rec10, _ = train_and_eval_experiment(
        exp_id="EXP-010-EMB-DIM-512",
        backbone="resnet18",
        embedding_dim=512,
        loss_name="contrastive",
        loss_margin=1.0,
        epochs=2,
        augmentor_type="baseline",
        preprocessor_method="otsu",
        device=device
    )

    # EXP-011 Hybrid Metric Loss
    rec11, _ = train_and_eval_experiment(
        exp_id="EXP-011-LOSS-HYBRID",
        backbone="resnet18",
        embedding_dim=256,
        loss_name="hybrid",
        loss_margin=1.0,
        alpha=1.0,
        beta=0.5,
        epochs=2,
        augmentor_type="baseline",
        preprocessor_method="otsu",
        device=device
    )

    # EXP-012 Combined Champion Candidate (Full Train Data, Hard Mining + Realistic Aug + Hybrid Loss)
    rec12, model_champ = train_and_eval_experiment(
        exp_id="EXP-012-CHAMPION-CANDIDATE",
        backbone="resnet18",
        embedding_dim=256,
        loss_name="hybrid",
        loss_margin=1.0,
        alpha=1.0,
        beta=0.5,
        epochs=3,
        max_train_samples=None,  # Full dataset
        augmentor_type="realistic",
        preprocessor_method="otsu",
        hard_negative_ratio=0.35,
        pair_balance_mode="standard",
        device=device
    )

    # Phase 13 Multi-Sample Reference Evaluation
    print("\n=======================================================")
    print("   PHASE 13: MULTI-SAMPLE REFERENCE AGGREGATION AUDIT")
    print("=======================================================")
    ref_results = evaluate_multi_reference_strategies(model_champ, device=device)
    ref_path = Path("artifacts/evaluation/multi_reference_validation_results.json")
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ref_path, "w", encoding="utf-8") as f:
        json.dump(ref_results, f, indent=2)
    print(f"[+] Saved multi-reference results to {ref_path}")
    for k, v in ref_results.items():
        print(f"  Strategy [{k:10s}] -> AUC: {v['roc_auc']:.4f} | EER: {v['eer']*100:.2f}% | Skilled FAR: {v['skilled_far']*100:.2f}% | TAR: {v['tar']*100:.2f}%")

    # Save Candidate Champion Checkpoint
    champ_pt_path = Path("artifacts/models/champion_candidate_model.pt")
    torch.save({
        "model_state_dict": model_champ.state_dict(),
        "embedding_dim": 256,
        "backbone": "resnet18",
        "optimal_threshold": rec12["validation_threshold"],
        "val_metrics": rec12
    }, champ_pt_path)
    print(f"[+] Saved candidate champion weights to: {champ_pt_path}")


if __name__ == "__main__":
    run_all_experiments()
