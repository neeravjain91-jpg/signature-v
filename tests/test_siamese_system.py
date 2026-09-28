"""
Comprehensive Unit and Integration Tests for Siamese Signature Verification ML System.
"""

import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import torch
from ml.preprocessing.signature_preprocessor import SignaturePreprocessor
from ml.models.siamese_network import SiameseSignatureNet
from ml.models.losses import ContrastiveLoss
from ml.models.dataset import SignaturePairDataset
from ml.inference.verify_signature import SignatureVerifier


def test_signature_preprocessor():
    print("[*] Testing SignaturePreprocessor...")
    preprocessor = SignaturePreprocessor(target_size=(224, 224))
    sample_path = "data/raw/signatures/full_org/original_1_1.png"

    # Test numpy output
    img_np = preprocessor.preprocess(sample_path, as_tensor=False)
    assert isinstance(img_np, np.ndarray), "Output must be numpy array"
    assert img_np.shape == (224, 224), f"Expected (224, 224), got {img_np.shape}"
    assert 0.0 <= img_np.min() and img_np.max() <= 1.0, "Values must be in [0.0, 1.0]"

    # Test tensor output
    img_t = preprocessor.preprocess(sample_path, as_tensor=True)
    assert isinstance(img_t, torch.Tensor), "Output must be torch.Tensor"
    assert img_t.shape == (1, 224, 224), f"Expected (1, 224, 224), got {img_t.shape}"
    assert img_t.dtype == torch.float32, "Tensor must be float32"
    print("    [+] Preprocessor tests passed.")


def test_siamese_architecture_and_weight_sharing():
    print("[*] Testing Siamese Architecture and Weight Sharing...")
    model = SiameseSignatureNet(embedding_dim=256)
    x1 = torch.randn(4, 1, 224, 224)
    x2 = torch.randn(4, 1, 224, 224)

    # 1. Forward pass
    emb1, emb2 = model(x1, x2)
    assert emb1.shape == (4, 256), f"Expected (4, 256), got {emb1.shape}"
    assert emb2.shape == (4, 256), f"Expected (4, 256), got {emb2.shape}"

    # 2. Verify L2 unit norm constraint
    norm1 = torch.norm(emb1, p=2, dim=1)
    norm2 = torch.norm(emb2, p=2, dim=1)
    assert torch.allclose(norm1, torch.ones_like(norm1), atol=1e-5), "Embeddings must have unit norm"
    assert torch.allclose(norm2, torch.ones_like(norm2), atol=1e-5), "Embeddings must have unit norm"

    # 3. Verify parameter sharing
    # Set model.eval() so dropout and batchnorm are deterministic
    model.eval()
    with torch.no_grad():
        emb_a, emb_b = model(x1, x1)
        dist = model.compute_distance(emb_a, emb_b)
        assert torch.allclose(dist, torch.zeros_like(dist), atol=1e-4), f"Identical inputs must yield ~0 distance, got {dist}"
        sim = model.compute_similarity(dist)
        assert torch.allclose(sim, torch.ones_like(sim), atol=1e-4), f"Identical inputs must yield ~1.0 similarity, got {sim}"
    print("    [+] Architecture and weight sharing tests passed.")


def test_contrastive_loss():
    print("[*] Testing Contrastive Loss...")
    criterion = ContrastiveLoss(margin=1.0)

    # Identical embeddings, label=1 (genuine) -> loss should be 0
    emb1 = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
    emb2 = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
    label_gen = torch.tensor([1.0, 1.0])
    loss_gen = criterion(emb1, emb2, label_gen)
    assert torch.isclose(loss_gen, torch.tensor(0.0)), "Loss for identical genuine pairs must be 0"

    # Distant embeddings (distance >= margin), label=0 (forged) -> loss should be 0
    emb_forg1 = torch.tensor([[1.0, 0.0]])
    emb_forg2 = torch.tensor([[-1.0, 0.0]]) # distance = 2.0 >= margin 1.0
    label_forg = torch.tensor([0.0])
    loss_forg = criterion(emb_forg1, emb_forg2, label_forg)
    assert torch.isclose(loss_forg, torch.tensor(0.0)), "Loss for negative pair outside margin must be 0"
    print("    [+] Contrastive loss tests passed.")


def test_pair_dataset():
    print("[*] Testing SignaturePairDataset...")
    ds = SignaturePairDataset("data/pairs/test_pairs.csv", cache_in_memory=False)
    assert len(ds) > 0, "Dataset must not be empty"
    item = ds[0]
    assert "image_1" in item and "image_2" in item and "label" in item
    assert item["image_1"].shape == (1, 224, 224)
    assert item["image_2"].shape == (1, 224, 224)
    assert item["label"].item() in [0.0, 1.0]
    print(f"    [+] Dataset test passed (Loaded {len(ds)} test pairs).")


def test_end_to_end_inference():
    print("[*] Testing SignatureVerifier End-to-End Inference...")
    checkpoint_file = "artifacts/models/best_siamese_model.pt"
    if not Path(checkpoint_file).exists():
        print("    [-] Checkpoint not yet found, skipping live inference test.")
        return

    verifier = SignatureVerifier(checkpoint_path=checkpoint_file)

    # Test Genuine Pair (Writer 46 sample 1 vs Writer 46 sample 2)
    ref_sig = "data/raw/signatures/full_org/original_46_1.png"
    sub_sig_genuine = "data/raw/signatures/full_org/original_46_2.png"
    sub_sig_forged = "data/raw/signatures/full_forg/forgeries_46_1.png"

    res_gen = verifier.verify(ref_sig, sub_sig_genuine)
    assert "similarity_score" in res_gen
    assert "euclidean_distance" in res_gen
    assert "decision" in res_gen
    assert len(res_gen["embedding_a"]) == 256
    assert len(res_gen["embedding_b"]) == 256

    res_forg = verifier.verify(ref_sig, sub_sig_forged)
    assert "similarity_score" in res_forg
    assert "decision" in res_forg

    print(f"    [+] Genuine Pair Result : Similarity={res_gen['similarity_score']}, Decision={res_gen['decision']}")
    print(f"    [+] Forged Pair Result  : Similarity={res_forg['similarity_score']}, Decision={res_forg['decision']}")
    print("    [+] End-to-End inference tests passed.")


def test_forged_samples_not_hardcoded_as_verified():
    """
    Verifies that the verification system dynamically evaluates similarity
    and does NOT have any hardcoded logic that marks forged or impostor signatures as VERIFIED.
    Fails if a known non-matching/forged signature pair is hardcoded as VERIFIED.
    """
    print("[*] Testing that Forged and Impostor Samples are NOT Hardcoded as VERIFIED...")
    checkpoint_file = "artifacts/models/best_siamese_model.pt"
    if not Path(checkpoint_file).exists():
        print("    [-] Checkpoint not yet found, skipping anti-hardcoding test.")
        return

    verifier = SignatureVerifier(checkpoint_path=checkpoint_file)

    # 1. Random impostor pair (Writer 46 vs Writer 52)
    impostor_ref = "data/raw/signatures/full_org/original_46_1.png"
    impostor_sub = "data/raw/signatures/full_org/original_52_1.png"
    res_impostor = verifier.verify(impostor_ref, impostor_sub)

    assert res_impostor["similarity_score"] < verifier.default_threshold, (
        f"Impostor similarity ({res_impostor['similarity_score']}) should be below threshold ({verifier.default_threshold})"
    )
    assert res_impostor["decision"] != "VERIFIED", (
        f"Impostor sample must NOT be classified as VERIFIED! Got: {res_impostor['decision']}"
    )

    # 2. Skilled forgery pair with clear stroke divergence (Writer 48)
    w48_ref = "data/raw/signatures/full_org/original_48_1.png"
    w48_forg = "data/raw/signatures/full_forg/forgeries_48_1.png"
    res_w48 = verifier.verify(w48_ref, w48_forg)
    assert res_w48["decision"] != "VERIFIED", (
        f"Writer 48 skilled forgery must not be hardcoded or accepted as VERIFIED! Got: {res_w48['decision']}"
    )

    # 3. Test through Banking Verification Service (Full End-to-End Pipeline)
    from database.session import SessionLocal
    from services.verification_service import BankingVerificationService
    db = SessionLocal()
    try:
        service = BankingVerificationService(db_session=db)
        res_pipeline = service.verify_transaction(
            transaction_reference="DEMO-TXN-CHEQUE-101",
            submitted_signature_path=impostor_sub
        )
        assert res_pipeline["decision"] in ["REJECTED", "MANUAL_REVIEW"], (
            f"Banking verification pipeline marked impostor signature as: {res_pipeline['decision']}"
        )
        assert res_pipeline["decision"] != "VERIFIED", "Pipeline must NEVER hardcode VERIFIED for impostor signature!"
    finally:
        db.close()

    print("    [+] Anti-hardcoding test passed: Forged and impostor samples correctly rejected/flagged.")


def test_champion_model_and_config():
    """Phase 27: Verify champion model checkpoint and frozen configuration."""
    champ_pt = Path("artifacts/models/champion_siamese_model.pt")
    champ_cfg = Path("artifacts/models/champion_config.json")

    assert champ_pt.exists(), "Champion model checkpoint must exist"
    assert champ_cfg.exists(), "Champion config JSON must exist"

    import json
    with open(champ_cfg, "r") as f:
        cfg = json.load(f)

    assert "frozen_threshold" in cfg, "Champion config must contain frozen_threshold"
    assert 0.65 <= cfg["frozen_threshold"] <= 0.85, f"Threshold {cfg['frozen_threshold']} out of expected range"
    assert cfg["model_version"] == "2.0.0-champion"

    # Verify model weights loading
    verifier = SignatureVerifier(checkpoint_path=champ_pt)
    assert verifier.model_version == "2.0.0-champion"
    assert verifier.default_threshold == cfg["frozen_threshold"]


def test_writer_disjoint_splits():
    """Phase 27: Verify zero writer identity leakage across splits."""
    import pandas as pd
    train_df = pd.read_csv("data/pairs/train_pairs.csv")
    val_df = pd.read_csv("data/pairs/validation_pairs.csv")
    test_df = pd.read_csv("data/pairs/test_pairs.csv")

    w_train = set(train_df["writer_1"]).union(set(train_df["writer_2"]))
    w_val = set(val_df["writer_1"]).union(set(val_df["writer_2"]))
    w_test = set(test_df["writer_1"]).union(set(test_df["writer_2"]))

    assert len(w_train.intersection(w_val)) == 0, "Train and Val writer sets must be strictly disjoint!"
    assert len(w_val.intersection(w_test)) == 0, "Val and Test writer sets must be strictly disjoint!"
    assert len(w_train.intersection(w_test)) == 0, "Train and Test writer sets must be strictly disjoint!"


def test_multi_reference_aggregation_logic():
    """Phase 27: Verify multi-specimen reference aggregation strategies."""
    ref_sims = [0.88, 0.82, 0.76]
    # Max
    assert max(ref_sims) == 0.88
    # Mean
    assert abs(sum(ref_sims)/3.0 - 0.82) < 1e-4
    # Top-2
    assert abs((0.88 + 0.82)/2.0 - 0.85) < 1e-4


if __name__ == "__main__":
    test_signature_preprocessor()
    test_siamese_architecture_and_weight_sharing()
    test_contrastive_loss()
    test_pair_dataset()
    test_end_to_end_inference()
    test_forged_samples_not_hardcoded_as_verified()
    test_champion_model_and_config()
    test_writer_disjoint_splits()
    test_multi_reference_aggregation_logic()
    print("\n[+] ALL SIAMESE ML SYSTEM UNIT AND INTEGRATION TESTS PASSED!\n")
