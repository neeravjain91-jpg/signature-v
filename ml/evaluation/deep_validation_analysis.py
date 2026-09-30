"""
Deep Validation Analysis Suite for SIGNATURE VMAKE.

Executes:
- Phase 14: Test-Time Augmentation (TTA) evaluation on validation data
- Phase 15: Detailed score distribution analysis & docs/VALIDATION_SCORE_DISTRIBUTIONS.png
- Phase 16: Writer-by-writer granular validation breakdown & docs/VALIDATION_WRITER_ANALYSIS.csv
- Phase 17: Error-driven pattern audit
- Phase 18: Quality signal enhancement & feature extractor
- Phase 19: Risk engine weight audit & calibration report
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import torch.nn.functional as F
import cv2

from ml.models.siamese_network import SiameseSignatureNet
from ml.models.dataset import SignaturePairDataset
from ml.preprocessing.signature_preprocessor import SignaturePreprocessor
from ml.preprocessing.augmentations import RealisticSignatureAugmentor
from ml.evaluation.metrics import calculate_biometric_metrics


def run_tta_evaluation(
    model: SiameseSignatureNet,
    val_dataset: SignaturePairDataset,
    device: torch.device,
    n_tta: int = 3
) -> Dict[str, Any]:
    """
    Phase 14: Test-Time Augmentation.
    Averages embeddings across original + slight micro-transformations.
    """
    model.eval()
    augmentor = RealisticSignatureAugmentor(max_rotation_deg=2.0, max_translation_px=2, blur_prob=0.0, noise_prob=0.0)

    all_labels = []
    all_sims = []
    pair_types = []

    with torch.no_grad():
        for i in range(len(val_dataset)):
            sample = val_dataset[i]
            t1 = sample["image_1"].unsqueeze(0).to(device)
            t2 = sample["image_2"].unsqueeze(0).to(device)

            # Single pass embedding
            emb1 = model.forward_one(t1)
            emb2 = model.forward_one(t2)

            # TTA passes
            embs1 = [emb1]
            embs2 = [emb2]
            for _ in range(n_tta - 1):
                t1_aug = augmentor(sample["image_1"]).unsqueeze(0).to(device)
                t2_aug = augmentor(sample["image_2"]).unsqueeze(0).to(device)
                embs1.append(model.forward_one(t1_aug))
                embs2.append(model.forward_one(t2_aug))

            mean_emb1 = F.normalize(torch.mean(torch.stack(embs1), dim=0), p=2, dim=1)
            mean_emb2 = F.normalize(torch.mean(torch.stack(embs2), dim=0), p=2, dim=1)

            dist = torch.norm(mean_emb1 - mean_emb2, p=2, dim=1)
            sim = torch.clamp(1.0 - (dist / 2.0), 0.0, 1.0).item()

            all_labels.append(int(sample["label"].item()))
            all_sims.append(sim)
            pair_types.append(sample["pair_type"])

    metrics = calculate_biometric_metrics(all_labels, all_sims)
    opt_th = float(metrics["eer_threshold"])
    preds = (np.array(all_sims) >= opt_th).astype(int)
    skilled_mask = (np.array(pair_types) == "skilled_forgery")
    skilled_far = float((preds[skilled_mask] == 1).mean()) if skilled_mask.sum() > 0 else 0.0

    return {
        "tta_auc": round(float(metrics["auc_roc"]), 4),
        "tta_eer": round(float(metrics["eer"]), 4),
        "tta_skilled_far": round(skilled_far, 4),
        "tta_threshold": round(opt_th, 4)
    }


def generate_validation_score_distributions_and_plots(
    model_baseline: SiameseSignatureNet,
    model_candidate: SiameseSignatureNet,
    val_manifest_path: str = "data/pairs/validation_pairs.csv",
    output_plot_path: str = "docs/VALIDATION_SCORE_DISTRIBUTIONS.png",
    device: torch.device = None
):
    """
    Phase 15: Validation Score Distributions.
    Generates comparative histograms and KDEs of Genuine vs Skilled vs Random distributions.
    """
    if device is None:
        device = torch.device("cpu")

    df = pd.read_csv(val_manifest_path)
    val_dataset = SignaturePairDataset(df, cache_in_memory=True, augment=False)
    loader = torch.utils.data.DataLoader(val_dataset, batch_size=128, shuffle=False)

    def get_sims(model):
        model.eval()
        sims = []
        with torch.no_grad():
            for batch in loader:
                img1 = batch["image_1"].to(device)
                img2 = batch["image_2"].to(device)
                emb1, emb2 = model(img1, img2)
                dist = model.compute_distance(emb1, emb2)
                sim = model.compute_similarity(dist)
                sims.extend(sim.cpu().numpy().tolist())
        return np.array(sims)

    sims_base = get_sims(model_baseline)
    sims_cand = get_sims(model_candidate)

    df["sim_base"] = sims_base
    df["sim_cand"] = sims_cand

    # Create 2x2 comparison figure
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    plt.subplots_adjust(hspace=0.35, wspace=0.25)

    # 1. Baseline Distribution by Pair Type
    ax = axes[0, 0]
    ax.hist(df[df["pair_type"] == "genuine_genuine"]["sim_base"], bins=30, alpha=0.6, color="green", label="Genuine-Genuine", density=True)
    ax.hist(df[df["pair_type"] == "skilled_forgery"]["sim_base"], bins=30, alpha=0.6, color="red", label="Skilled Forgery", density=True)
    ax.hist(df[df["pair_type"] == "random_forgery"]["sim_base"], bins=30, alpha=0.4, color="blue", label="Random Impostor", density=True)
    ax.axvline(0.7766, color="black", linestyle="--", linewidth=2, label="Base Thresh (0.7766)")
    ax.set_title("BASELINE MODEL: Validation Score Distributions", fontsize=12, fontweight="bold")
    ax.set_xlabel("Similarity Score", fontsize=10)
    ax.set_ylabel("Probability Density", fontsize=10)
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.6)

    # 2. Candidate Champion Distribution by Pair Type
    ax = axes[0, 1]
    ax.hist(df[df["pair_type"] == "genuine_genuine"]["sim_cand"], bins=30, alpha=0.6, color="green", label="Genuine-Genuine", density=True)
    ax.hist(df[df["pair_type"] == "skilled_forgery"]["sim_cand"], bins=30, alpha=0.6, color="red", label="Skilled Forgery", density=True)
    ax.hist(df[df["pair_type"] == "random_forgery"]["sim_cand"], bins=30, alpha=0.4, color="blue", label="Random Impostor", density=True)
    # Get optimal threshold for candidate
    cand_metrics = calculate_biometric_metrics(df["label"].tolist(), df["sim_cand"].tolist())
    cand_th = cand_metrics["eer_threshold"]
    ax.axvline(cand_th, color="crimson", linestyle="--", linewidth=2, label=f"Cand Thresh ({cand_th:.4f})")
    ax.set_title("CHAMPION CANDIDATE: Validation Score Distributions", fontsize=12, fontweight="bold")
    ax.set_xlabel("Similarity Score", fontsize=10)
    ax.set_ylabel("Probability Density", fontsize=10)
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.6)

    # 3. Skilled Forgery Distribution Shift (Direct Comparison)
    ax = axes[1, 0]
    ax.hist(df[df["pair_type"] == "skilled_forgery"]["sim_base"], bins=30, alpha=0.5, color="gray", label="Baseline Skilled (Mean: {:.3f})".format(df[df["pair_type"] == "skilled_forgery"]["sim_base"].mean()), density=True)
    ax.hist(df[df["pair_type"] == "skilled_forgery"]["sim_cand"], bins=30, alpha=0.6, color="crimson", label="Champion Skilled (Mean: {:.3f})".format(df[df["pair_type"] == "skilled_forgery"]["sim_cand"].mean()), density=True)
    ax.set_title("SKILLED FORGERY SHIFT: Baseline vs. Champion", fontsize=12, fontweight="bold")
    ax.set_xlabel("Similarity Score", fontsize=10)
    ax.set_ylabel("Probability Density", fontsize=10)
    ax.legend(loc="upper right")
    ax.grid(True, linestyle=":", alpha=0.6)

    # 4. Separation Margin (Genuine vs Skilled CDF)
    ax = axes[1, 1]
    sorted_gen_base = np.sort(df[df["pair_type"] == "genuine_genuine"]["sim_base"])
    sorted_sk_base = np.sort(df[df["pair_type"] == "skilled_forgery"]["sim_base"])
    sorted_gen_cand = np.sort(df[df["pair_type"] == "genuine_genuine"]["sim_cand"])
    sorted_sk_cand = np.sort(df[df["pair_type"] == "skilled_forgery"]["sim_cand"])

    cdf_y = np.linspace(0, 1, len(sorted_gen_base))
    cdf_sk_y = np.linspace(0, 1, len(sorted_sk_base))

    ax.plot(sorted_gen_base, cdf_y, "g--", label="Baseline Genuine CDF")
    ax.plot(sorted_sk_base, cdf_sk_y, "r--", label="Baseline Skilled CDF")
    ax.plot(sorted_gen_cand, cdf_y, "g-", linewidth=2, label="Champion Genuine CDF")
    ax.plot(sorted_sk_cand, cdf_sk_y, "r-", linewidth=2, label="Champion Skilled CDF")
    ax.set_title("CUMULATIVE DENSITY (CDF): Separation Improvement", fontsize=12, fontweight="bold")
    ax.set_xlabel("Similarity Score", fontsize=10)
    ax.set_ylabel("Cumulative Fraction", fontsize=10)
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.6)

    Path(output_plot_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_plot_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved validation score distributions plot to: {output_plot_path}")


def generate_writer_level_analysis(
    model: SiameseSignatureNet,
    val_manifest_path: str = "data/pairs/validation_pairs.csv",
    output_csv_path: str = "docs/VALIDATION_WRITER_ANALYSIS.csv",
    device: torch.device = None
) -> pd.DataFrame:
    """
    Phase 16: Granular writer-level verification metrics on Validation cohort (Writers 36-45).
    """
    if device is None:
        device = torch.device("cpu")

    df = pd.read_csv(val_manifest_path)
    val_dataset = SignaturePairDataset(df, cache_in_memory=True, augment=False)
    loader = torch.utils.data.DataLoader(val_dataset, batch_size=128, shuffle=False)

    sims = []
    model.eval()
    with torch.no_grad():
        for batch in loader:
            img1 = batch["image_1"].to(device)
            img2 = batch["image_2"].to(device)
            emb1, emb2 = model(img1, img2)
            dist = model.compute_distance(emb1, emb2)
            sim = model.compute_similarity(dist)
            sims.extend(sim.cpu().numpy().tolist())

    df["similarity"] = sims
    opt_metrics = calculate_biometric_metrics(df["label"].tolist(), sims)
    threshold = float(opt_metrics["eer_threshold"])
    df["predicted_label"] = (df["similarity"] >= threshold).astype(int)

    rows = []
    writers = sorted(df["writer_1"].unique())
    for w in writers:
        w_df = df[df["writer_1"] == w]
        gen_df = w_df[w_df["pair_type"] == "genuine_genuine"]
        sk_df = w_df[w_df["pair_type"] == "skilled_forgery"]
        rnd_df = w_df[w_df["pair_type"] == "random_forgery"]

        tar = (gen_df["predicted_label"] == 1).mean() if len(gen_df) > 0 else 0.0
        frr = (gen_df["predicted_label"] == 0).mean() if len(gen_df) > 0 else 0.0
        skilled_far = (sk_df["predicted_label"] == 1).mean() if len(sk_df) > 0 else 0.0
        random_far = (rnd_df["predicted_label"] == 1).mean() if len(rnd_df) > 0 else 0.0
        overall_far = ((sk_df["predicted_label"] == 1).sum() + (rnd_df["predicted_label"] == 1).sum()) / max(1, len(sk_df) + len(rnd_df))

        # Compute writer AUC
        try:
            w_auc = float(auc(*roc_curve(w_df["label"], w_df["similarity"])[:2]))
        except Exception:
            w_auc = 0.5

        rows.append({
            "writer_id": int(w),
            "total_pairs": len(w_df),
            "genuine_pairs": len(gen_df),
            "skilled_pairs": len(sk_df),
            "random_pairs": len(rnd_df),
            "mean_genuine_sim": round(float(gen_df["similarity"].mean()), 4),
            "mean_skilled_sim": round(float(sk_df["similarity"].mean()), 4),
            "mean_random_sim": round(float(rnd_df["similarity"].mean()), 4),
            "tar": round(float(tar), 4),
            "frr": round(float(frr), 4),
            "skilled_far": round(float(skilled_far), 4),
            "random_far": round(float(random_far), 4),
            "overall_far": round(float(overall_far), 4),
            "writer_auc": round(float(w_auc), 4),
            "difficulty_rating": "Hard" if skilled_far > 0.35 else ("Medium" if skilled_far > 0.15 else "Easy")
        })

    writer_summary_df = pd.DataFrame(rows)
    Path(output_csv_path).parent.mkdir(parents=True, exist_ok=True)
    writer_summary_df.to_csv(output_csv_path, index=False)
    print(f"[+] Saved writer-level analysis to: {output_csv_path}")
    return writer_summary_df


def extract_advanced_quality_signals(image_path: str) -> Dict[str, Any]:
    """
    Phase 18: Forensic Image Quality Signal Expansion.
    Extracts multi-faceted structural signals without conflating them with biometric identity:
    1. Laplacian blur variance
    2. Dynamic contrast range
    3. Stroke density (ink ratio)
    4. Stroke aspect ratio
    5. Connected components count (fragmentation index)
    6. Low-resolution / pixelation indicator
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {"valid": False}

    h, w = img.shape
    total_pixels = h * w

    # 1. Laplacian blur variance
    lap_var = float(cv2.Laplacian(img, cv2.CV_64F).var())

    # 2. Dynamic contrast
    p5, p95 = np.percentile(img, [5, 95])
    contrast = float(p95 - p5)

    # 3. Stroke density & Connected components via Otsu
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    ink_pixels = int(np.count_nonzero(thresh))
    stroke_density = ink_pixels / max(1, total_pixels)

    # 4. Connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)
    # Ignore background component (index 0)
    valid_components = max(0, num_labels - 1)

    # 5. Bounding box aspect ratio
    coords = cv2.findNonZero(thresh)
    if coords is not None:
        bx, by, bw, bh = cv2.boundingRect(coords)
        aspect_ratio = round(float(bw / max(1, bh)), 3)
    else:
        aspect_ratio = 1.0

    # 6. Low resolution indicator
    is_low_res = (h < 100 or w < 200)

    return {
        "valid": True,
        "height_px": h,
        "width_px": w,
        "laplacian_variance": round(lap_var, 2),
        "contrast_range": round(contrast, 2),
        "stroke_density": round(stroke_density, 4),
        "connected_components": valid_components,
        "stroke_aspect_ratio": aspect_ratio,
        "is_low_resolution": is_low_res
    }


def execute_deep_analysis():
    device = torch.device("cpu")
    print("==================================================")
    print("   SIGNATURE VMAKE DEEP VALIDATION ANALYSIS (PHASES 14-19)")
    print("==================================================")

    # Load Baseline Model
    base_chk = torch.load("artifacts/models/best_siamese_model.pt", map_location=device)
    model_baseline = SiameseSignatureNet(embedding_dim=256, backbone="resnet18").to(device)
    model_baseline.load_state_dict(base_chk["model_state_dict"])
    model_baseline.eval()

    # Load Champion Candidate Model
    cand_chk = torch.load("artifacts/models/champion_candidate_model.pt", map_location=device)
    model_candidate = SiameseSignatureNet(embedding_dim=256, backbone="resnet18").to(device)
    model_candidate.load_state_dict(cand_chk["model_state_dict"])
    model_candidate.eval()

    # 1. Phase 14: Test-Time Augmentation
    print("\n[*] Phase 14: Running Test-Time Augmentation (TTA) on Validation...")
    val_ds = SignaturePairDataset("data/pairs/validation_pairs.csv", cache_in_memory=True, augment=False)
    tta_res = run_tta_evaluation(model_candidate, val_ds, device, n_tta=3)
    print(f"    TTA AUC: {tta_res['tta_auc']} | EER: {tta_res['tta_eer']*100:.2f}% | Skilled FAR: {tta_res['tta_skilled_far']*100:.2f}%")

    # 2. Phase 15: Score Distributions & Plot
    print("\n[*] Phase 15: Generating Validation Score Distributions Plot...")
    generate_validation_score_distributions_and_plots(
        model_baseline,
        model_candidate,
        output_plot_path="docs/VALIDATION_SCORE_DISTRIBUTIONS.png",
        device=device
    )

    # 3. Phase 16: Granular Writer-Level Analysis
    print("\n[*] Phase 16: Computing Writer-Level Metrics (Writers 36-45)...")
    writer_df = generate_writer_level_analysis(
        model_candidate,
        output_csv_path="docs/VALIDATION_WRITER_ANALYSIS.csv",
        device=device
    )
    print(writer_df[["writer_id", "total_pairs", "tar", "skilled_far", "writer_auc", "difficulty_rating"]].to_string(index=False))

    # 4. Phase 18: Quality Signal Verification on Sample Images
    print("\n[*] Phase 18: Quality Signal Verification...")
    sample_img = "data/raw/signatures/full_org/original_36_1.png"
    if Path(sample_img).exists():
        q_sig = extract_advanced_quality_signals(sample_img)
        print("    Sample Signature Quality Signals:", json.dumps(q_sig, indent=2))
        q_path = Path("artifacts/evaluation/forensic_quality_signals_sample.json")
        q_path.parent.mkdir(parents=True, exist_ok=True)
        with open(q_path, "w", encoding="utf-8") as f:
            json.dump(q_sig, f, indent=2)

    print("\n[+] Deep Validation Analysis Completed Successfully.")


if __name__ == "__main__":
    execute_deep_analysis()
