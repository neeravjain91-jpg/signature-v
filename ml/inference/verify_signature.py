"""
Inference Engine for Intelligent Signature Verification.

Receives:
    Input A: Registered/Reference signature (specimen)
    Input B: New/Submitted signature (questioned cheque/voucher)

Produces:
    - embedding A
    - embedding B
    - distance (Euclidean metric)
    - similarity score (0.0 to 1.0)
    - verification decision (VERIFIED | MANUAL_REVIEW | REJECTED)
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from typing import Union, Dict, Any, Optional
import numpy as np
from PIL import Image
import torch

from ml.preprocessing.signature_preprocessor import SignaturePreprocessor
from ml.models.siamese_network import SiameseSignatureNet


class SignatureVerifier:
    """
    High-level inference engine for pair verification and embedding extraction.
    """

    def __init__(
        self,
        checkpoint_path: Union[str, Path] = "artifacts/models/best_siamese_model.pt",
        threshold: Optional[float] = None,
        device: Optional[str] = None
    ):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.preprocessor = SignaturePreprocessor(target_size=(224, 224))
        self.checkpoint_path = Path(checkpoint_path)

        if not self.checkpoint_path.exists():
            raise FileNotFoundError(
                f"Model checkpoint not found at: {self.checkpoint_path}. "
                "Please run `python ml/training/train.py` first."
            )

        checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
        embedding_dim = checkpoint.get("embedding_dim", 256)
        self.default_threshold = threshold or checkpoint.get("optimal_threshold", 0.7500)

        self.model = SiameseSignatureNet(
            embedding_dim=embedding_dim,
            default_threshold=self.default_threshold
        )
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()

    def extract_embedding(
        self,
        image_input: Union[str, Path, np.ndarray, Image.Image]
    ) -> np.ndarray:
        """
        Generates a 256-dimensional L2-normalized feature embedding for a signature.
        Used for database enrollment.
        """
        tensor = self.preprocessor.preprocess(image_input, as_tensor=True).to(self.device)
        if tensor.dim() == 3:
            tensor = tensor.unsqueeze(0)
        with torch.no_grad():
            embedding = self.model.forward_one(tensor)
        return embedding.squeeze(0).cpu().numpy()

    def verify(
        self,
        reference_input: Union[str, Path, np.ndarray, Image.Image],
        submitted_input: Union[str, Path, np.ndarray, Image.Image],
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Compares questioned signature against reference specimen.
        Returns:
            Dictionary containing similarity score, distance, embeddings, and decision.
        """
        thresh = threshold if threshold is not None else self.default_threshold

        t1 = self.preprocessor.preprocess(reference_input, as_tensor=True).to(self.device)
        t2 = self.preprocessor.preprocess(submitted_input, as_tensor=True).to(self.device)
        if t1.dim() == 3:
            t1 = t1.unsqueeze(0)
        if t2.dim() == 3:
            t2 = t2.unsqueeze(0)

        with torch.no_grad():
            emb1, emb2 = self.model.forward(t1, t2)
            distance = self.model.compute_distance(emb1, emb2).item()
            similarity = self.model.compute_similarity(torch.tensor([distance])).item()

        # Decision Logic with Borderline Manual Review Buffer
        manual_review_buffer = 0.10
        if similarity >= thresh:
            decision = "VERIFIED"
            risk_level = "LOW"
        elif similarity >= (thresh - manual_review_buffer):
            decision = "MANUAL_REVIEW"
            risk_level = "MEDIUM"
        else:
            decision = "REJECTED"
            risk_level = "HIGH"

        return {
            "similarity_score": round(similarity, 4),
            "euclidean_distance": round(distance, 4),
            "threshold_used": round(thresh, 4),
            "decision": decision,
            "risk_recommendation": risk_level,
            "embedding_a": emb1.squeeze(0).cpu().tolist(),
            "embedding_b": emb2.squeeze(0).cpu().tolist()
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Verify a pair of signatures")
    parser.add_argument("--ref", required=True, help="Path to reference signature")
    parser.add_argument("--sub", required=True, help="Path to submitted signature")
    parser.add_argument("--checkpoint", default="artifacts/models/best_siamese_model.pt")
    parser.add_argument("--threshold", type=float, default=None)
    args = parser.parse_args()

    verifier = SignatureVerifier(checkpoint_path=args.checkpoint, threshold=args.threshold)
    result = verifier.verify(args.ref, args.sub)
    print("\n--- Signature Verification Result ---")
    print(f"Similarity Score   : {result['similarity_score']}")
    print(f"Euclidean Distance : {result['euclidean_distance']}")
    print(f"Threshold Used     : {result['threshold_used']}")
    print(f"Decision           : {result['decision']}")
    print(f"Risk Level         : {result['risk_recommendation']}")
    print("--------------------------------------\n")


if __name__ == "__main__":
    main()
