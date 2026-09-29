"""
Customer-Conditioned Multi-Reference Signature Gallery Evaluator.

Simulates banking customer specimen vault workflows:
- Customer enrolls 3 genuine reference specimens.
- Computes intra-gallery baseline metrics (mean, variance, min, max).
- Evaluates questioned transactions against enrolled specimens using:
  A. Max similarity
  B. Top-k similarity mean (k=2)
  C. Median similarity
  D. Centroid similarity
  E. Gallery-variance-normalized z-score
  F. Robust customer-conditioned similarity score
- Tests genuine queries, skilled forgeries, and random cross-writer impostors
  with identical protocols to evaluate TAR, FRR, Skilled FAR, Random FAR, AUC, and EER.
"""

from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.metrics import roc_curve, auc

from ml.preprocessing.signature_preprocessor import SignaturePreprocessor
from ml.evaluation.metrics import calculate_biometric_metrics


class CustomerGalleryEvaluator:
    def __init__(
        self,
        model: torch.nn.Module,
        device: torch.device,
        preprocessor: SignaturePreprocessor = None,
        gallery_size: int = 3
    ):
        self.model = model.to(device)
        self.model.eval()
        self.device = device
        self.preprocessor = preprocessor or SignaturePreprocessor(target_size=(224, 224))
        self.gallery_size = gallery_size
        self._embedding_cache: Dict[str, torch.Tensor] = {}

    def get_embedding(self, image_path: Path) -> torch.Tensor:
        path_str = str(image_path).replace("\\", "/")
        if path_str in self._embedding_cache:
            return self._embedding_cache[path_str]

        tensor = self.preprocessor.preprocess(path_str, as_tensor=True).to(self.device)
        if tensor.dim() == 3:
            tensor = tensor.unsqueeze(0)

        with torch.no_grad():
            forward_fn = getattr(self.model, "forward_one", getattr(self.model, "forward_once", None))
            emb = forward_fn(tensor)
            emb = F.normalize(emb, p=2, dim=1)

        self._embedding_cache[path_str] = emb
        return emb

    def compute_similarity(self, emb1: torch.Tensor, emb2: torch.Tensor) -> float:
        dist = torch.norm(emb1 - emb2, p=2, dim=1).item()
        return 1.0 / (1.0 + dist)

    def evaluate_customer(
        self,
        writer_id: int,
        genuine_paths: List[Path],
        forged_paths: List[Path],
        random_impostor_paths: List[Path],
        strategy: str = "max"
    ) -> List[Dict[str, Any]]:
        """
        Evaluates a single customer's gallery against:
        - Query genuine samples (samples remaining after enrollment)
        - Skilled forgery samples
        - Random impostor samples
        """
        assert len(genuine_paths) >= self.gallery_size + 1, f"Writer {writer_id} needs at least {self.gallery_size + 1} genuine signatures"

        # 1. Enrolled Reference Specimens
        enrolled_paths = genuine_paths[:self.gallery_size]
        query_genuine_paths = genuine_paths[self.gallery_size:]

        enrolled_embs = [self.get_embedding(p) for p in enrolled_paths]
        enrolled_tensor = torch.cat(enrolled_embs, dim=0)  # (K, D)

        # 2. Customer Intra-Gallery Baseline
        intra_sims = []
        for i in range(len(enrolled_embs)):
            for j in range(i + 1, len(enrolled_embs)):
                s = self.compute_similarity(enrolled_embs[i], enrolled_embs[j])
                intra_sims.append(s)

        intra_mean = float(np.mean(intra_sims)) if intra_sims else 0.85
        intra_std = max(float(np.std(intra_sims)), 0.01) if intra_sims else 0.03
        intra_min = float(np.min(intra_sims)) if intra_sims else 0.80

        # Centroid embedding
        centroid_emb = F.normalize(enrolled_tensor.mean(dim=0, keepdim=True), p=2, dim=1)

        def score_query(q_emb: torch.Tensor) -> float:
            sims = [self.compute_similarity(q_emb, r_emb) for r_emb in enrolled_embs]
            sims_arr = np.array(sims)

            if strategy == "max":
                return float(np.max(sims_arr))
            elif strategy == "top_k_mean":
                top_k = min(2, len(sims_arr))
                return float(np.mean(np.sort(sims_arr)[-top_k:]))
            elif strategy == "median":
                return float(np.median(sims_arr))
            elif strategy == "centroid":
                return self.compute_similarity(q_emb, centroid_emb)
            elif strategy == "variance_normalized":
                raw_max = float(np.max(sims_arr))
                z = (raw_max - intra_mean) / intra_std
                # Sigmoidal mapping to [0, 1] centered around z=0
                return float(1.0 / (1.0 + np.exp(-z)))
            elif strategy == "customer_conditioned":
                raw_max = float(np.max(sims_arr))
                # Conditioned scoring: how closely raw_max aligns with customer's self-similarity band
                # If query matches or exceeds customer's intra_min, score is elevated; if lower, penalized sharply
                margin_offset = raw_max - intra_min
                scale = max(2.0 * intra_std, 0.04)
                conditioned = 0.5 + 0.5 * np.tanh(margin_offset / scale)
                # Combine raw max with conditioned ratio
                return float(0.6 * raw_max + 0.4 * conditioned)
            else:
                return float(np.max(sims_arr))

        results = []

        # Evaluate genuine queries (label = 1)
        for p in query_genuine_paths:
            q_emb = self.get_embedding(p)
            score = score_query(q_emb)
            results.append({
                "writer_id": writer_id,
                "label": 1,
                "pair_type": "genuine_genuine",
                "score": score,
                "intra_mean": intra_mean,
                "intra_std": intra_std
            })

        # Evaluate skilled forgeries (label = 0)
        for p in forged_paths:
            q_emb = self.get_embedding(p)
            score = score_query(q_emb)
            results.append({
                "writer_id": writer_id,
                "label": 0,
                "pair_type": "skilled_forgery",
                "score": score,
                "intra_mean": intra_mean,
                "intra_std": intra_std
            })

        # Evaluate random impostors (label = 0)
        for p in random_impostor_paths:
            q_emb = self.get_embedding(p)
            score = score_query(q_emb)
            results.append({
                "writer_id": writer_id,
                "label": 0,
                "pair_type": "random_forgery",
                "score": score,
                "intra_mean": intra_mean,
                "intra_std": intra_std
            })

        return results

    def evaluate_cohort(
        self,
        writers: List[int],
        gen_by_writer: Dict[int, List[Path]],
        forg_by_writer: Dict[int, List[Path]],
        strategy: str = "max"
    ) -> Dict[str, Any]:
        all_evals = []
        for w in writers:
            g_paths = sorted(gen_by_writer[w])
            f_paths = sorted(forg_by_writer[w])

            # Random impostors drawn from other writers in the cohort
            other_writers = [ow for ow in writers if ow != w]
            random_paths = []
            for ow in other_writers:
                if len(gen_by_writer[ow]) > 3:
                    random_paths.append(gen_by_writer[ow][3])  # Sample 4
            # Keep sample count balanced to ~ 20-24 random impostors
            random_paths = random_paths[:len(f_paths)]

            evals = self.evaluate_customer(
                writer_id=w,
                genuine_paths=g_paths,
                forged_paths=f_paths,
                random_impostor_paths=random_paths,
                strategy=strategy
            )
            all_evals.extend(evals)

        df = pd.DataFrame(all_evals)
        y_true = df["label"].values
        y_scores = df["score"].values
        types = df["pair_type"].values

        metrics = calculate_biometric_metrics(y_true.tolist(), y_scores.tolist())
        eer_thresh = float(metrics["eer_threshold"])
        eer = float(metrics["eer"])
        auc_val = float(metrics["auc_roc"])

        preds = (y_scores >= eer_thresh).astype(int)
        tar = float((preds[types == "genuine_genuine"] == 1).mean())
        frr = float((preds[types == "genuine_genuine"] == 0).mean())
        sk_far = float((preds[types == "skilled_forgery"] == 1).mean())
        rnd_far = float((preds[types == "random_forgery"] == 1).mean())
        overall_far = float((preds[y_true == 0] == 1).mean())

        return {
            "strategy": strategy,
            "eer_threshold": round(eer_thresh, 4),
            "roc_auc": round(auc_val, 4),
            "eer": round(eer, 4),
            "tar": round(tar, 4),
            "frr": round(frr, 4),
            "skilled_far": round(sk_far, 4),
            "random_far": round(rnd_far, 4),
            "overall_far": round(overall_far, 4),
            "total_samples": len(df),
            "genuine_count": int((y_true == 1).sum()),
            "impostor_count": int((y_true == 0).sum())
        }
