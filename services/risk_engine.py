"""
Multi-Factor Fraud Risk Assessment Engine for Banking Transactions.

Synthesizes:
1. Siamese Neural Network Similarity Component
2. Forensic Image Quality & Degradation Component (Laplacian Blur & Contrast)
3. Transaction Monetary & Channel Risk Component
4. Customer Behavioral & Velocity Risk Component

Produces:
- Weighted Composite Risk Score (0.0000 - 1.0000)
- Categorical Risk Level (LOW, MEDIUM, HIGH)
- Explainable Risk Factor Audit Codes
"""

from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal
import cv2
import numpy as np


class FraudRiskEngine:
    """
    Production-grade risk scoring engine combining biometric inference with financial context.
    """

    # Default weights for composite calculation
    DEFAULT_WEIGHTS = {
        "similarity": 0.50,
        "image_quality": 0.15,
        "transaction_risk": 0.25,
        "behavioral": 0.10
    }

    # Transaction type risk baselines
    TXN_TYPE_FACTORS = {
        "FORM_VERIFICATION": 0.10,
        "CHEQUE": 0.25,
        "WITHDRAWAL": 0.40,
        "AUTHORIZATION": 0.50,
        "WIRE_TRANSFER": 0.70
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS
        # Normalize weights
        total = sum(self.weights.values())
        self.weights = {k: v / total for k, v in self.weights.items()}

    @staticmethod
    def assess_image_quality(image_array: np.ndarray) -> float:
        """
        Assesses physical capture quality via Laplacian variance (blur detection) and contrast.
        Returns a score in [0.0, 1.0], where 1.0 is sharp and clean.
        """
        if image_array is None or image_array.size == 0:
            return 0.0

        if image_array.ndim == 3:
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_array

        # 1. Blur detection via Laplacian variance
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        # Benchmark scale: variance > 500 is sharp; < 80 is severely blurred
        blur_score = np.clip(laplacian_var / 500.0, 0.05, 1.0)

        # 2. Dynamic range / contrast
        p5, p95 = np.percentile(gray, [5, 95])
        contrast_range = float(p95 - p5)
        contrast_score = np.clip(contrast_range / 180.0, 0.1, 1.0)

        composite_quality = 0.7 * blur_score + 0.3 * contrast_score
        return round(float(composite_quality), 4)

    def calculate_transaction_risk(
        self,
        amount: float,
        transaction_type: str
    ) -> Tuple[float, List[Dict[str, str]]]:
        """
        Computes financial risk factor based on transaction amount and channel severity.
        """
        risk_factors = []
        base_type_factor = self.TXN_TYPE_FACTORS.get(transaction_type.upper(), 0.30)

        # Tiered monetary risk scaling
        amt = float(amount)
        if amt <= 1000.0:
            amt_factor = 0.10
        elif amt <= 5000.0:
            amt_factor = 0.25
        elif amt <= 25000.0:
            amt_factor = 0.55
            risk_factors.append({
                "code": "HIGH_VALUE_TIER",
                "description": f"Transaction amount (${amt:,.2f}) exceeds standard retail threshold ($10,000)."
            })
        elif amt <= 100000.0:
            amt_factor = 0.80
            risk_factors.append({
                "code": "CRITICAL_VALUE_TIER",
                "description": f"High-risk corporate tier transaction (${amt:,.2f}) requiring dual authorization."
            })
        else:
            amt_factor = 1.00
            risk_factors.append({
                "code": "MEGA_VALUE_TRANSACTION",
                "description": f"Exceptional transaction volume (${amt:,.2f}) exceeding $100,000."
            })

        if transaction_type.upper() in ["WIRE_TRANSFER", "WITHDRAWAL"]:
            risk_factors.append({
                "code": f"IRREVERSIBLE_CHANNEL_{transaction_type.upper()}",
                "description": f"Transaction initiated via immediate/irreversible settlement channel ({transaction_type})."
            })

        composite_txn_risk = 0.65 * amt_factor + 0.35 * base_type_factor
        return round(min(1.0, composite_txn_risk), 4), risk_factors

    def evaluate(
        self,
        similarity_score: float,
        model_threshold: float,
        image_quality_score: float,
        amount: float,
        transaction_type: str,
        behavioral_score: float = 0.05,
        customer_history_anomalies: int = 0
    ) -> Dict[str, Any]:
        """
        Executes complete multi-factor fraud risk evaluation.
        """
        factors: List[Dict[str, str]] = []

        # 1. Similarity Risk Component (1 - similarity)
        sim = float(similarity_score)
        thresh = float(model_threshold)
        similarity_risk = float(np.clip(1.0 - sim, 0.0, 1.0))

        if sim < (thresh - 0.12):
            factors.append({
                "code": "SEVERE_STROKE_DISCREPANCY",
                "description": f"Similarity score ({sim:.4f}) is substantially below model threshold ({thresh:.4f}). High probability of forgery."
            })
        elif sim < thresh:
            factors.append({
                "code": "BORDERLINE_SIMILARITY_MATCH",
                "description": f"Similarity score ({sim:.4f}) is marginally below threshold ({thresh:.4f}). Potential natural variation or skilled forgery."
            })
        else:
            factors.append({
                "code": "AUTHENTIC_STROKE_CORRELATION",
                "description": f"Signature exhibits high biometric correlation ({sim:.4f}) exceeding threshold ({thresh:.4f})."
            })

        # 2. Image Quality Component (1 - quality)
        img_q = float(image_quality_score)
        quality_risk = float(np.clip(1.0 - img_q, 0.0, 1.0))
        if img_q < 0.50:
            factors.append({
                "code": "POOR_SCAN_RESOLUTION",
                "description": f"Image quality score ({img_q:.4f}) indicates significant blur or low scan contrast."
            })

        # 3. Transaction Risk Component
        txn_risk, txn_factors = self.calculate_transaction_risk(amount, transaction_type)
        factors.extend(txn_factors)

        # 4. Behavioral Component
        beh_risk = float(behavioral_score)
        if customer_history_anomalies > 0:
            beh_risk = min(1.0, beh_risk + customer_history_anomalies * 0.20)
            factors.append({
                "code": "HISTORICAL_FRAUD_FLAGS",
                "description": f"Customer account has {customer_history_anomalies} recorded verification anomalies in past 90 days."
            })

        # 5. Composite Weighted Risk Score
        overall_risk = (
            self.weights["similarity"] * similarity_risk +
            self.weights["image_quality"] * quality_risk +
            self.weights["transaction_risk"] * txn_risk +
            self.weights["behavioral"] * beh_risk
        )
        overall_risk = round(float(np.clip(overall_risk, 0.0, 1.0)), 4)

        # 6. Categorical Risk Classification
        if overall_risk < 0.25:
            risk_level = "LOW"
        elif overall_risk < 0.60:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        # 7. Operational Decision Recommendation
        if sim >= thresh and risk_level == "LOW":
            recommended_decision = "VERIFIED"
        elif sim >= (thresh - 0.12) or risk_level == "MEDIUM":
            recommended_decision = "MANUAL_REVIEW"
        else:
            recommended_decision = "REJECTED"

        return {
            "similarity_component": round(similarity_risk, 4),
            "image_quality_component": round(quality_risk, 4),
            "transaction_risk_component": round(txn_risk, 4),
            "behavioral_component": round(beh_risk, 4),
            "overall_risk_score": overall_risk,
            "risk_level": risk_level,
            "recommended_decision": recommended_decision,
            "risk_factors": factors
        }
