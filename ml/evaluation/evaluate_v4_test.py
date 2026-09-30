"""
Final Frozen Test Evaluation for SIGNATURE VMAKE v4 on Writers 46-55.

Evaluates:
1. Single-Pair Verification on the canonical 1,200 pairs using frozen threshold tau* = 0.5924
2. Customer Gallery Verification (3 enrolled specimens per customer) using frozen gallery threshold tau_gal* = 0.6312
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ml.models.architectures import SiameseResNet18
from ml.models.dataset import SignaturePairDataset
from ml.preprocessing.signature_preprocessor import SignaturePreprocessor
from ml.evaluation.customer_gallery_evaluator import CustomerGalleryEvaluator
from ml.evaluation.metrics import calculate_biometric_metrics

MODEL_PATH = Path("artifacts/models/v4_champion_model.pt")
THRESH_PATH = Path("artifacts/models/v4_champion_threshold.json")
TEST_PAIRS_PATH = Path("data/pairs/test_pairs.csv")
OUT_DIR = Path("artifacts/evaluation")
DOCS_DIR = Path("docs")


def evaluate_v4_test():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    device = torch.device("cpu")

    # Load frozen threshold and weights
    with open(THRESH_PATH, "r", encoding="utf-8") as f:
        tdata = json.load(f)
    tau_single = float(tdata["single_pair_threshold"])
    tau_gallery = float(tdata["gallery_threshold"])

    chk = torch.load(MODEL_PATH, map_location=device)
    model = SiameseResNet18(embedding_dim=256, in_channels=1).to(device)
    model.load_state_dict(chk["model_state_dict"])
    model.eval()

    preprocessor = SignaturePreprocessor(binarization_method="otsu", target_size=(224, 224))

    print("==================================================")
    print("   SIGNATURE VMAKE v4 FINAL FROZEN TEST EVALUATION")
    print("   Cohort: CEDAR Writers 46-55 (Strictly Withheld)")
    print("==================================================")
    print(f"[*] Frozen Single-Pair Threshold (tau*)    : {tau_single:.4f}")
    print(f"[*] Frozen Gallery Threshold (tau_gal*)    : {tau_gallery:.4f}")

    # ==================================================
    # 1. SINGLE-PAIR FROZEN TEST EVALUATION
    # ==================================================
    from torch.utils.data import DataLoader
    test_df = pd.read_csv(TEST_PAIRS_PATH)
    test_ds = SignaturePairDataset(test_df, preprocessor=preprocessor, cache_in_memory=True, augment=False)
    test_loader = DataLoader(test_ds, batch_size=128, shuffle=False)

    sims, labels, types = [], [], []
    with torch.no_grad():
        for b in test_loader:
            e1, e2 = model(b["image_1"].to(device), b["image_2"].to(device))
            dist = model.compute_distance(e1, e2)
            s = model.compute_similarity(dist)
            sims.extend(s.cpu().numpy().tolist())
            labels.extend(b["label"].cpu().numpy().tolist())
            types.extend(b["pair_type"])

    y_test = np.array(labels)
    s_test = np.array(sims)
    types_test = np.array(types)

    m_single = calculate_biometric_metrics(labels, sims)
    preds_single = (s_test >= tau_single).astype(int)

    acc = float(accuracy_score(y_test, preds_single))
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, preds_single, average="binary", zero_division=0)
    tar = float((preds_single[types_test == "genuine_genuine"] == 1).mean())
    frr = float((preds_single[types_test == "genuine_genuine"] == 0).mean())
    sk_far = float((preds_single[types_test == "skilled_forgery"] == 1).mean())
    rnd_far = float((preds_single[types_test == "random_forgery"] == 1).mean())
    overall_far = float((preds_single[y_test == 0] == 1).mean())

    single_results = {
        "evaluation_mode": "Single-Pair",
        "frozen_threshold": tau_single,
        "auc_roc": round(float(m_single["auc_roc"]), 4),
        "eer": round(float(m_single["eer"]), 4),
        "accuracy": round(acc, 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "tar": round(tar, 4),
        "frr": round(frr, 4),
        "skilled_forgery_far": round(sk_far, 4),
        "random_impostor_far": round(rnd_far, 4),
        "overall_far": round(overall_far, 4),
        "confusion_matrix": {
            "tp": int(((preds_single == 1) & (y_test == 1)).sum()),
            "fp": int(((preds_single == 1) & (y_test == 0)).sum()),
            "tn": int(((preds_single == 0) & (y_test == 0)).sum()),
            "fn": int(((preds_single == 0) & (y_test == 1)).sum()),
            "total": len(y_test)
        }
    }

    with open(OUT_DIR / "v4_single_pair_test_results.json", "w", encoding="utf-8") as f:
        json.dump(single_results, f, indent=2)

    print("\n--------------------------------------------------")
    print("   PART 1: SINGLE-PAIR TEST RESULTS (Writers 46-55)")
    print("--------------------------------------------------")
    print(f"[*] ROC-AUC             : {single_results['auc_roc']:.4f}")
    print(f"[*] EER                 : {single_results['eer']*100:.2f}%")
    print(f"[*] TAR                 : {single_results['tar']*100:.2f}%")
    print(f"[*] FRR                 : {single_results['frr']*100:.2f}%")
    print(f"[*] Overall FAR         : {single_results['overall_far']*100:.2f}%")
    print(f"[*] Skilled Forgery FAR : {single_results['skilled_forgery_far']*100:.2f}%")
    print(f"[*] Random Impostor FAR : {single_results['random_impostor_far']*100:.2f}%")
    print(f"[*] Accuracy / F1-Score : {single_results['accuracy']*100:.2f}% / {single_results['f1_score']:.4f}")

    # ==================================================
    # 2. CUSTOMER GALLERY FROZEN TEST EVALUATION
    # ==================================================
    gen_by_w = defaultdict(list)
    forg_by_w = defaultdict(list)
    for p in Path("data/processed").glob("*/*/*.png"):
        w_id = int(p.stem.split("_")[1])
        if 46 <= w_id <= 55:
            if "genuine" in str(p):
                gen_by_w[w_id].append(p)
            elif "forged" in str(p):
                forg_by_w[w_id].append(p)

    evaluator = CustomerGalleryEvaluator(model, device=device, gallery_size=3)
    test_writers = sorted(list(gen_by_w.keys()))

    # Collect individual query evaluations across all test customers
    all_gallery_evals = []
    for w in test_writers:
        g_paths = sorted(gen_by_w[w])
        f_paths = sorted(forg_by_w[w])

        other_w = [ow for ow in test_writers if ow != w]
        rnd_paths = []
        for ow in other_w:
            if len(gen_by_w[ow]) > 3:
                rnd_paths.append(gen_by_w[ow][3])
        rnd_paths = rnd_paths[:len(f_paths)]

        evals = evaluator.evaluate_customer(
            writer_id=w,
            genuine_paths=g_paths,
            forged_paths=f_paths,
            random_impostor_paths=rnd_paths,
            strategy="max"
        )
        all_gallery_evals.extend(evals)

    gal_df = pd.DataFrame(all_gallery_evals)
    y_gal = gal_df["label"].values
    s_gal = gal_df["score"].values
    types_gal = gal_df["pair_type"].values

    m_gal = calculate_biometric_metrics(y_gal.tolist(), s_gal.tolist())
    preds_gal = (s_gal >= tau_gallery).astype(int)

    acc_gal = float(accuracy_score(y_gal, preds_gal))
    prec_gal, rec_gal, f1_gal, _ = precision_recall_fscore_support(y_gal, preds_gal, average="binary", zero_division=0)
    tar_gal = float((preds_gal[types_gal == "genuine_genuine"] == 1).mean())
    frr_gal = float((preds_gal[types_gal == "genuine_genuine"] == 0).mean())
    sk_far_gal = float((preds_gal[types_gal == "skilled_forgery"] == 1).mean())
    rnd_far_gal = float((preds_gal[types_gal == "random_forgery"] == 1).mean())
    overall_far_gal = float((preds_gal[y_gal == 0] == 1).mean())

    gallery_results = {
        "evaluation_mode": "3-Specimen Customer Gallery (max similarity)",
        "enrolled_specimens_per_customer": 3,
        "frozen_threshold": tau_gallery,
        "auc_roc": round(float(m_gal["auc_roc"]), 4),
        "eer": round(float(m_gal["eer"]), 4),
        "accuracy": round(acc_gal, 4),
        "precision": round(float(prec_gal), 4),
        "recall": round(float(rec_gal), 4),
        "f1_score": round(float(f1_gal), 4),
        "tar": round(tar_gal, 4),
        "frr": round(frr_gal, 4),
        "skilled_forgery_far": round(sk_far_gal, 4),
        "random_impostor_far": round(rnd_far_gal, 4),
        "overall_far": round(overall_far_gal, 4),
        "confusion_matrix": {
            "tp": int(((preds_gal == 1) & (y_gal == 1)).sum()),
            "fp": int(((preds_gal == 1) & (y_gal == 0)).sum()),
            "tn": int(((preds_gal == 0) & (y_gal == 0)).sum()),
            "fn": int(((preds_gal == 0) & (y_gal == 1)).sum()),
            "total": len(y_gal)
        }
    }

    with open(OUT_DIR / "v4_gallery_test_results.json", "w", encoding="utf-8") as f:
        json.dump(gallery_results, f, indent=2)

    print("\n--------------------------------------------------")
    print("   PART 2: CUSTOMER GALLERY TEST RESULTS (Writers 46-55)")
    print("--------------------------------------------------")
    print(f"[*] ROC-AUC             : {gallery_results['auc_roc']:.4f}")
    print(f"[*] EER                 : {gallery_results['eer']*100:.2f}%")
    print(f"[*] TAR                 : {gallery_results['tar']*100:.2f}%")
    print(f"[*] FRR                 : {gallery_results['frr']*100:.2f}%")
    print(f"[*] Overall FAR         : {gallery_results['overall_far']*100:.2f}%")
    print(f"[*] Skilled Forgery FAR : {gallery_results['skilled_forgery_far']*100:.2f}%")
    print(f"[*] Random Impostor FAR : {gallery_results['random_impostor_far']*100:.2f}%")
    print(f"[*] Accuracy / F1-Score : {gallery_results['accuracy']*100:.2f}% / {gallery_results['f1_score']:.4f}")

    # Generate Comparison ROC Plot
    from sklearn.metrics import roc_curve
    fpr_sp, tpr_sp, _ = roc_curve(y_test, s_test)
    fpr_gal, tpr_gal, _ = roc_curve(y_gal, s_gal)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr_sp, tpr_sp, label=f"Single-Pair (AUC = {single_results['auc_roc']:.4f})", color="royalblue", lw=2)
    plt.plot(fpr_gal, tpr_gal, label=f"3-Specimen Gallery (AUC = {gallery_results['auc_roc']:.4f})", color="crimson", lw=2.5)
    plt.plot([0, 1], [0, 1], "k--", alpha=0.5)
    plt.xlabel("False Positive Rate (FAR)", fontsize=11)
    plt.ylabel("True Positive Rate (TAR)", fontsize=11)
    plt.title("SIGNATURE VMAKE v4 Frozen Test ROC: Single-Pair vs. Customer Gallery", fontsize=12, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="lower right", fontsize=10)
    plt.tight_layout()
    plot_path = DOCS_DIR / "V4_TEST_ROC_CURVE.png"
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"\n[+] Saved test ROC plot to: {plot_path}")


if __name__ == "__main__":
    evaluate_v4_test()
