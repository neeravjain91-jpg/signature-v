# REPRODUCIBILITY GUIDE & PIPELINE EXECUTION COMMANDS
**SYNAPSE — Intelligent Signature Verification Platform**
*Phase 29: Complete Deterministic Pipeline Reproduction Guide*
*Date: September 28, 2026 | Environment: Python 3.11.9, PyTorch 2.13.0+cpu, Windows x64*

---

## 1. System Environment & Dependencies

| Specification | Configuration |
|---|---|
| **Operating System** | Windows 11 x64 |
| **Python Runtime** | Python 3.11.9 |
| **Deep Learning Framework** | PyTorch 2.13.0+cpu |
| **Computer Vision** | OpenCV 5.0.0 (`opencv-python-headless`), Pillow 12.3.0 |
| **Data & Scientific Libraries** | NumPy 2.4.6, Pandas 2.3.3, Scikit-Learn 1.8.0, SciPy 1.17.1 |
| **Backend Framework** | FastAPI 0.141.1, Uvicorn 0.52.4, SQLAlchemy 2.1.1 |
| **Global Random Seed** | `42` (ensures identical dataset shuffling, weight initialization, and mining) |

---

## 2. End-to-End Pipeline Reproduction Commands

### Step 1: Dataset Verification & Pair Manifest Generation
```bash
# Verify raw dataset files (Writers 1-55, 2640 signatures)
python ml/data/validate_dataset.py

# Generate writer-disjoint pairs (Train: W1-35, Val: W36-45, Test: W46-55)
python ml/data/create_pairs.py
```

### Step 2: Baseline Model Training
```bash
# Train baseline Siamese ResNet-18 model with contrastive loss
python ml/training/train.py \
    --train-pairs data/pairs/train_pairs.csv \
    --val-pairs data/pairs/validation_pairs.csv \
    --output-dir artifacts/models \
    --epochs 4 \
    --batch-size 32 \
    --lr 0.0003 \
    --embedding-dim 256 \
    --margin 1.0
```

### Step 3: Baseline Threshold Calibration (Validation Data Only)
```bash
# Calibrate operating threshold strictly on validation cohort (Writers 36-45)
python ml/evaluation/calibrate_threshold.py \
    --checkpoint artifacts/models/best_siamese_model.pt \
    --val-pairs data/pairs/validation_pairs.csv \
    --output artifacts/models/calibrated_threshold.json \
    --plot docs/VAL_CALIBRATION_CURVES.png
```

### Step 4: Systematic Validation Experimentation Suite
```bash
# Run all 12 controlled ablation experiments (HNM, Augmentation, Preprocessing, Backbones, Losses)
python ml/experiments/run_experiments.py
```

### Step 5: Deep Validation Diagnostics (Phases 14–19)
```bash
# Run TTA, score distribution analysis, writer-level metrics, and image quality checks
python ml/evaluation/deep_validation_analysis.py
```

### Step 6: Final Frozen Test Evaluation (Writers 46–55)
```bash
# Evaluate frozen Champion model on test cohort
python ml/evaluation/evaluate.py \
    --checkpoint artifacts/models/champion_siamese_model.pt \
    --calibrated-threshold artifacts/models/champion_config.json \
    --test-pairs data/pairs/test_pairs.csv \
    --output artifacts/evaluation/champion_test_evaluation_results.json \
    --roc-plot docs/CHAMPION_ROC_CURVE.png \
    --far-frr-plot docs/CHAMPION_FAR_FRR_CURVE.png \
    --dist-plot docs/CHAMPION_SCORE_DISTRIBUTIONS.png \
    --fa-cases artifacts/evaluation/champion_fa_cases.json \
    --fr-cases artifacts/evaluation/champion_fr_cases.json \
    --batch-size 64
```

### Step 7: Writer 46 Case Study Verification
```bash
# Evaluate specific Writer 46 forensic case study
python ml/experiments/check_writer_46.py
```

### Step 8: Automated Regression Testing
```bash
# Run complete test suite (17/17 tests passing)
pytest -v tests/
```

### Step 9: Launch Banking API & Web Dashboard
```bash
# Start FastAPI backend at http://localhost:8000
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
