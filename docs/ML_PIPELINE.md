# SIGNATURE VMAKE — Machine Learning Pipeline Architecture

**Document Version:** 1.0.0  
**Project:** SIGNATURE VMAKE (`signature-vmake`)  
**Domain:** End-to-End Biometric Verification & Fraud Assessment Pipeline  

---

## 1. High-Level Pipeline Flowchart

The end-to-end pipeline in SIGNATURE VMAKE coordinates data processing, representation learning, multi-factor risk evaluation, and database auditing:

```mermaid
flowchart TD
    subgraph STAGE_1 ["1. Image Acquisition & Ingestion"]
        RAW["Raw Specimen Image<br/>(PNG, JPEG, TIFF)"] --> VAL["Image Validator<br/>• MIME check<br/>• Size caps (<=5MB)<br/>• Format integrity"]
    end

    subgraph STAGE_2 ["2. Computer Vision Preprocessing"]
        VAL --> GRAY["Grayscale Conversion<br/>(cv2.cvtColor)"]
        GRAY --> DENOISE["Gaussian Smoothing<br/>(k=3 kernel)"]
        DENOISE --> OTSU["Otsu Binarization<br/>(Dark stroke on light bg)"]
        OTSU --> BBOX["Bounding Box Extraction<br/>(Contours + 10px padding)"]
        BBOX --> PAD["Aspect-Preserved Resizing<br/>(Centering to 224x224)"]
        PAD --> NORM["Float32 Normalization<br/>(Pixel values in [0.0, 1.0])"]
    end

    subgraph STAGE_3 ["3. Pluggable Model Verification"]
        NORM --> DISPATCH{"Active Model Verifier<br/>(SignatureVerificationModel)"}
        DISPATCH -->|Track A| SKL["Classical Sklearn<br/>• 264-d HOG & Morphology<br/>• RBF SVM Posterior"]
        DISPATCH -->|Track B| VIT["HF Vision Transformer<br/>• 196 Patch Self-Attention<br/>• Metric Projection Head"]
        DISPATCH -->|Track C| SIA["Siamese ResNet Champion<br/>• Conv-residual layers<br/>• 256-d Unit Hypersphere"]
        SKL & VIT & SIA --> EMB["Signature Embeddings / Distance<br/>||u - v||_2"]
    end

    subgraph STAGE_4 ["4. Biometric Decision & Confidence"]
        EMB --> SIM["Similarity Metric Computation<br/>S = 1 / (1 + D)"]
        SIM --> CALIB["Calibrated Decision Boundary<br/>(Validation-tuned EER threshold)"]
        CALIB --> DEC["Decision Engine<br/>• VERIFIED (S >= Threshold + Margin)<br/>• MANUAL_REVIEW (Borderline)<br/>• REJECTED (S < Threshold - Margin)"]
    end

    subgraph STAGE_5 ["5. Multi-Factor Fraud Risk Engine"]
        DEC --> Q_SIG["Laplacian Image Quality"]
        DEC --> T_SIG["Transaction Monetary Tier"]
        DEC --> B_SIG["Behavioral History Factor"]
        Q_SIG & T_SIG & B_SIG --> RISK["Composite Fraud Risk Score<br/>(0.0000 to 1.0000)"]
    end

    subgraph STAGE_6 ["6. Relational Persistence & Audit"]
        RISK --> DB_LOG[("PostgreSQL / SQLite Database<br/>• verification_attempts<br/>• risk_assessments<br/>• audit_logs")]
        DB_LOG --> API_RESP["FastAPI JSON Response"]
    end
```

---

## 2. Preprocessing & Normalization Protocol

Implemented in [`ml/preprocessing/signature_preprocessor.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/preprocessing/signature_preprocessor.py):
1. **Grayscale Standardization:** Converts RGBA, RGB, or indexed scans to single-channel 8-bit grayscale with alpha blending against a synthetic white background.
2. **Noise Reduction:** Applies a $3 \times 3$ Gaussian blur to eliminate scanner sensor grain without smearing delicate stroke endpoints.
3. **Adaptive / Otsu Binarization:** Automatically calculates the optimal bimodal gray-level split threshold to cleanly isolate foreground ink from paper backgrounds.
4. **Bounding Box Isolation:** Identifies connected stroke contours, crops tightly around the outer bounding box with a 10-pixel safety margin to discard dead white space.
5. **Aspect-Ratio Preserved Resizing:** Scales the cropped signature proportionally to fit within a $224 \times 224$ canvas, centering with padding to prevent artificial geometric distortion.
6. **Float32 Normalization:** Maps pixel intensities to the interval $[0.0, 1.0]$.

---

## 3. Pluggable Model Architecture

All model tracks implement the abstract base class [`ml/models/model_interface.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/models/model_interface.py):
* `extract_features(image) -> np.ndarray`
* `compute_distance(feat1, feat2) -> float`
* `compute_similarity(distance) -> float`
* `verify_pair(ref, query, threshold) -> VerificationOutput`
* `verify_gallery(gallery, query, strategy, threshold) -> VerificationOutput`

### 3.1 Multiple Reference Galleries
When a bank customer registers multiple signature specimens ($N \ge 1$), evidence is aggregated via:
- **Maximum Similarity (`max_similarity`):** Optimistic matching against the customer's best specimen.
- **Mean Similarity (`mean_similarity`):** Smooths natural intra-signer variance across all specimens.
- **Top-$K$ Mean (`top_k_mean`):** Averages the top 2 closest specimens.
- **Centroid Distance (`centroid_distance`):** Computes Euclidean distance against the unit-normalized gallery centroid.

---

## 4. Multi-Factor Banking Fraud Risk Engine

The system does not rely exclusively on biometrics. The business risk engine ([`services/risk_engine.py`](file:///c:/Users/ASUS/Downloads/hcl/services/risk_engine.py)) combines 4 orthogonal vectors:

$$R_{\text{composite}} = w_{\text{bio}} R_{\text{bio}} + w_{\text{qual}} R_{\text{qual}} + w_{\text{txn}} R_{\text{txn}} + w_{\text{beh}} R_{\text{beh}}$$

where:
* $R_{\text{bio}} = 1.0 - S_{\text{biometric}}$ (biometric dissimilarity).
* $R_{\text{qual}} = 1.0 - Q_{\text{image}}$ (Laplacian blur variance and contrast penalty).
* $R_{\text{txn}}$: Transaction amount risk (e.g. $\$100\text{k}+$ wire transfers vs $\$50$ counter cheques).
* $R_{\text{beh}}$: Velocity and historical anomaly penalty.
* Weights: $w_{\text{bio}} = 0.50$, $w_{\text{qual}} = 0.15$, $w_{\text{txn}} = 0.25$, $w_{\text{beh}} = 0.10$.
