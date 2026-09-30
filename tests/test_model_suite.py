"""
Pytest Suite for SIGNATURE VMAKE Model Suite & Interface Compliance:
- Preprocessing & Morphological extraction
- Model Track A: Classical scikit-learn SVM Baseline
- Model Track B: Hugging Face Vision Transformer (ViT)
- Model Track C: Siamese ResNet Verifier
- Multi-Reference Gallery Evidence Aggregation
- Biometric Evaluation Metrics & Calibration
"""

import sys
import numpy as np
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.preprocessing.signature_preprocessor import SignaturePreprocessor
from ml.models.model_interface import SignatureVerificationModel, VerificationOutput
from ml.baselines.feature_extractor import ClassicalFeatureExtractor
from ml.baselines.classical_classifier import ClassicalSklearnVerifier
from ml.models.transformer_signature_model import VisionTransformerVerifier, VisionTransformerSignatureNet
from ml.inference.verify_signature import get_model_verifier
from ml.evaluation.metrics import calculate_biometric_metrics


def test_signature_preprocessor_pipeline():
    preprocessor = SignaturePreprocessor(target_size=(224, 224))
    # Create synthetic test canvas with a black stroke
    canvas = np.ones((300, 500), dtype=np.uint8) * 255
    canvas[100:150, 150:350] = 20  # dark stroke

    processed = preprocessor.preprocess(canvas)
    assert processed.shape == (224, 224)
    assert processed.dtype == np.float32
    assert 0.0 <= np.min(processed) <= np.max(processed) <= 1.0


def test_classical_feature_extractor():
    extractor = ClassicalFeatureExtractor()
    sample_path = "data/raw/signatures/full_org/original_46_1.png"
    if Path(sample_path).exists():
        feat = extractor.extract(sample_path)
    else:
        dummy = np.ones((224, 224), dtype=np.uint8) * 255
        dummy[50:100, 50:150] = 0
        feat = extractor.extract(dummy)

    assert isinstance(feat, np.ndarray)
    assert feat.shape == (264,)
    # Assert L2 normalized unit length
    norm = np.linalg.norm(feat)
    assert abs(norm - 1.0) < 1e-4


def test_classical_sklearn_verifier():
    verifier = ClassicalSklearnVerifier()
    assert isinstance(verifier, SignatureVerificationModel)
    assert verifier.model_type == "CLASSICAL_SKLEARN"

    sample_1 = "data/raw/signatures/full_org/original_46_1.png"
    sample_2 = "data/raw/signatures/full_org/original_46_2.png"

    if Path(sample_1).exists() and Path(sample_2).exists():
        output = verifier.verify_pair(sample_1, sample_2)
        assert isinstance(output, VerificationOutput)
        assert 0.0 <= output.similarity_score <= 1.0
        assert 0.0 <= output.confidence <= 1.0
        assert output.decision in ("VERIFIED", "REJECTED", "MANUAL_REVIEW")


def test_huggingface_vision_transformer_verifier():
    verifier = VisionTransformerVerifier()
    assert isinstance(verifier, SignatureVerificationModel)
    assert verifier.model_type == "VISION_TRANSFORMER"

    sample_1 = "data/raw/signatures/full_org/original_46_1.png"
    sample_2 = "data/raw/signatures/full_org/original_46_2.png"

    if Path(sample_1).exists() and Path(sample_2).exists():
        output = verifier.verify_pair(sample_1, sample_2)
        assert isinstance(output, VerificationOutput)
        assert 0.0 <= output.similarity_score <= 1.0
        assert output.model_name == "HF_Vision_Transformer"
        assert output.decision in ("VERIFIED", "REJECTED", "MANUAL_REVIEW")


def test_model_verifier_factory():
    for track, expected_type in [
        ("siamese", "SIAMESE_RESNET"),
        ("transformer", "VISION_TRANSFORMER"),
        ("sklearn", "CLASSICAL_SKLEARN")
    ]:
        v = get_model_verifier(track)
        assert isinstance(v, SignatureVerificationModel)
        assert v.model_type == expected_type


def test_multi_reference_gallery_verification():
    verifier = get_model_verifier("transformer")
    sample_refs = [
        "data/raw/signatures/full_org/original_46_1.png",
        "data/raw/signatures/full_org/original_46_3.png"
    ]
    query = "data/raw/signatures/full_org/original_46_2.png"

    if all(Path(p).exists() for p in sample_refs + [query]):
        # Test max_similarity strategy
        out_max = verifier.verify_gallery(sample_refs, query, strategy="max_similarity")
        assert isinstance(out_max, VerificationOutput)
        assert out_max.reference_count == 2
        assert 0.0 <= out_max.similarity_score <= 1.0

        # Test mean_similarity strategy
        out_mean = verifier.verify_gallery(sample_refs, query, strategy="mean_similarity")
        assert isinstance(out_mean, VerificationOutput)
        assert 0.0 <= out_mean.similarity_score <= 1.0


def test_biometric_metrics_calculation():
    # Perfectly separated predictions
    y_true = np.array([1, 1, 1, 1, 0, 0, 0, 0])
    sims = np.array([0.9, 0.85, 0.8, 0.75, 0.3, 0.25, 0.2, 0.15])

    metrics = calculate_biometric_metrics(y_true, sims)
    assert metrics["auc_roc"] == 1.0
    assert metrics["accuracy"] == 1.0
    assert metrics["far"] == 0.0
    assert metrics["frr"] == 0.0
    assert metrics["eer"] == 0.0
