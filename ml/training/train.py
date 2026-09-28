"""
Training Pipeline for Siamese Signature Verification Neural Network.

Executes contrastive metric learning with automatic GPU/CPU selection,
validation monitoring, EER calculation, and model checkpointing.
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import torch
from torch.utils.data import DataLoader
from ml.models.siamese_network import SiameseSignatureNet
from ml.models.losses import ContrastiveLoss
from ml.models.dataset import SignaturePairDataset
from ml.evaluation.metrics import calculate_biometric_metrics


def train_siamese_network(
    train_pairs_path: str = "data/pairs/train_pairs.csv",
    val_pairs_path: str = "data/pairs/validation_pairs.csv",
    output_dir: str = "artifacts/models",
    epochs: int = 5,
    batch_size: int = 32,
    lr: float = 1e-4,
    embedding_dim: int = 256,
    margin: float = 1.0,
    max_train_samples: int = None,
    max_val_samples: int = None
):
    # 1. Device selection
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("==================================================")
    print("   SIAMESE SIGNATURE VERIFICATION TRAINING")
    print("==================================================")
    print(f"[*] Execution Device       : {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU Fallback'})")
    print(f"[*] Target Architecture    : Siamese ResNet Encoder (Weights Shared)")
    print(f"[*] Embedding Dimension    : {embedding_dim}")
    print(f"[*] Contrastive Margin     : {margin}")
    print(f"[*] Batch Size             : {batch_size}")
    print(f"[*] Base Learning Rate     : {lr}")
    print(f"[*] Target Epochs          : {epochs}")

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 2. Datasets & Loaders
    print(f"\n[*] Loading Training Pairs from: {train_pairs_path}")
    train_dataset = SignaturePairDataset(train_pairs_path, cache_in_memory=True, augment=True)
    if max_train_samples and len(train_dataset) > max_train_samples:
        train_dataset.df = train_dataset.df.iloc[:max_train_samples]
    print(f"[+] Loaded {len(train_dataset)} training pairs.")

    print(f"[*] Loading Validation Pairs from: {val_pairs_path}")
    val_dataset = SignaturePairDataset(val_pairs_path, cache_in_memory=True, augment=False)
    if max_val_samples and len(val_dataset) > max_val_samples:
        val_dataset.df = val_dataset.df.iloc[:max_val_samples]
    print(f"[+] Loaded {len(val_dataset)} validation pairs.")

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # 3. Model, Criterion, Optimizer
    model = SiameseSignatureNet(embedding_dim=embedding_dim).to(device)
    criterion = ContrastiveLoss(margin=margin).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=1)

    best_val_loss = float("inf")
    best_eer = float("inf")
    best_threshold = 0.75
    history = []

    start_time = time.time()

    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        # --- TRAIN PHASE ---
        model.train()
        running_train_loss = 0.0
        train_batches = 0

        for batch in train_loader:
            img1 = batch["image_1"].to(device)
            img2 = batch["image_2"].to(device)
            labels = batch["label"].to(device)

            optimizer.zero_grad()
            emb1, emb2 = model(img1, img2)
            loss = criterion(emb1, emb2, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            running_train_loss += loss.item()
            train_batches += 1

        avg_train_loss = running_train_loss / max(1, train_batches)

        # --- VALIDATION PHASE ---
        model.eval()
        running_val_loss = 0.0
        val_batches = 0
        all_labels = []
        all_sims = []

        with torch.no_grad():
            for batch in val_loader:
                img1 = batch["image_1"].to(device)
                img2 = batch["image_2"].to(device)
                labels = batch["label"].to(device)

                emb1, emb2 = model(img1, img2)
                loss = criterion(emb1, emb2, labels)
                running_val_loss += loss.item()
                val_batches += 1

                dist = model.compute_distance(emb1, emb2)
                sim = model.compute_similarity(dist)

                all_labels.extend(labels.cpu().numpy().tolist())
                all_sims.extend(sim.cpu().numpy().tolist())

        avg_val_loss = running_val_loss / max(1, val_batches)
        val_metrics = calculate_biometric_metrics(all_labels, all_sims)
        scheduler.step(avg_val_loss)

        epoch_duration = time.time() - epoch_start
        print(f"Epoch [{epoch:02d}/{epochs:02d}] ({epoch_duration:.1f}s) | "
              f"Train Loss: {avg_train_loss:.4f} | "
              f"Val Loss: {avg_val_loss:.4f} | "
              f"Val EER: {val_metrics['eer']*100:.2f}% | "
              f"Val AUC: {val_metrics['auc_roc']:.4f} | "
              f"Optimal Thresh: {val_metrics['eer_threshold']:.4f}")

        epoch_record = {
            "epoch": epoch,
            "train_loss": avg_train_loss,
            "val_loss": avg_val_loss,
            "val_eer": val_metrics["eer"],
            "val_auc": val_metrics["auc_roc"],
            "eer_threshold": val_metrics["eer_threshold"],
            "duration_sec": epoch_duration
        }
        history.append(epoch_record)

        # Save checkpoint if best validation loss
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            best_eer = val_metrics["eer"]
            best_threshold = val_metrics["eer_threshold"]

            checkpoint_file = out_path / "best_siamese_model.pt"
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "embedding_dim": embedding_dim,
                "optimal_threshold": best_threshold,
                "best_val_loss": best_val_loss,
                "best_eer": best_eer,
                "val_metrics": {k: v for k, v in val_metrics.items() if k != "roc_curve"}
            }, checkpoint_file)
            print(f"    --> [Checkpoint] Saved new best model to: {checkpoint_file}")

    total_time = time.time() - start_time
    print("\n==================================================")
    print("           TRAINING RUN COMPLETED")
    print("==================================================")
    print(f"[+] Total Duration         : {total_time:.2f} seconds")
    print(f"[+] Best Validation Loss   : {best_val_loss:.4f}")
    print(f"[+] Best Validation EER    : {best_eer*100:.2f}%")
    print(f"[+] Recommended Threshold  : {best_threshold:.4f}")
    print(f"[+] Model Weights Saved    : {out_path / 'best_siamese_model.pt'}")

    # Save summary
    summary_file = out_path / "training_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_duration_sec": total_time,
            "device": str(device),
            "best_val_loss": best_val_loss,
            "best_eer": best_eer,
            "optimal_threshold": best_threshold,
            "epochs_trained": epochs,
            "history": history
        }, f, indent=2)
    print(f"[+] Training Summary Saved : {summary_file}")
    print("==================================================\n")

    return checkpoint_file, best_threshold


def main():
    parser = argparse.ArgumentParser(description="Train Siamese Signature Verification Network")
    parser.add_argument("--epochs", type=int, default=5, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--embedding-dim", type=int, default=256, help="Embedding dimension")
    parser.add_argument("--margin", type=float, default=1.0, help="Contrastive loss margin")
    parser.add_argument("--max-train-pairs", type=int, default=None, help="Limit number of train pairs")
    parser.add_argument("--max-val-pairs", type=int, default=None, help="Limit number of val pairs")
    args = parser.parse_args()

    train_siamese_network(
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        embedding_dim=args.embedding_dim,
        margin=args.margin,
        max_train_samples=args.max_train_pairs,
        max_val_samples=args.max_val_pairs
    )


if __name__ == "__main__":
    main()
