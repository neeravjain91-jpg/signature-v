# REPRODUCIBILITY GUIDE & PIPELINE EXECUTION COMMANDS
**SIGNATURE VMAKE — Intelligent Signature Verification Platform**
*Phase 24: Complete Deterministic Pipeline Reproduction Guide (PowerShell Compatible)*
*Date: September 28, 2026 | Environment: Python 3.11.9, PyTorch 2.13.0+cpu, Windows x64*

---

## 1. System Environment & Hardware Configuration

| Environment Field | Value |
|---|---|
| **Operating System** | Windows 11 Home / Pro (x64) |
| **Shell Environment** | Windows PowerShell 5.1 / PowerShell 7+ |
| **Python Version** | Python 3.11.9 |
| **PyTorch Version** | PyTorch 2.13.0+cpu |
| **TorchVision Version** | TorchVision 0.29.0+cpu |
| **CUDA Available** | `False` (CPU-Optimized execution using `torch.set_num_threads(4)`) |
| **Primary Dependencies** | FastAPI 0.141.1, SQLAlchemy 2.1.1, OpenCV 5.0.0, Scikit-Learn 1.8.0, Pandas 2.3.3 |
| **Global Random Seed** | `42` |
| **Dataset Configuration** | CEDAR Offline Signature Benchmark (55 Writers, 2,640 images) |
| **Split Allocation** | Train: Writers 1–35 (7,000 pairs), Val: Writers 36–45 (1,200 pairs), Test: Writers 46–55 (1,200 pairs) |

---

## 2. Deterministic Pipeline Reproduction (10 Steps)

### Step 1: Dataset Verification & Pair Generation
```powershell
python ml/data/validate_dataset.py
python ml/data/create_pairs.py
```

### Step 2: Baseline Model Training
```powershell
python ml/training/train.py --train-pairs data/pairs/train_pairs.csv --val-pairs data/pairs/validation_pairs.csv --output-dir artifacts/models --epochs 4 --batch-size 32 --lr 0.0003 --embedding-dim 256 --margin 1.0
```

### Step 3: Systematic Ablation Experiments Reproduction
```powershell
python ml/experiments/run_experiments.py
```

### Step 4: Champion Model Clean Retraining
```powershell
python ml/training/train_champion.py
```

### Step 5: Validation Threshold Calibration
```powershell
python ml/evaluation/calibrate_threshold.py --checkpoint artifacts/models/champion_siamese_model.pt --val-pairs data/pairs/validation_pairs.csv --output artifacts/models/champion_threshold.json --plot docs/VAL_CALIBRATION_CURVES.png
```

### Step 6: Validation Evaluation Reconfirmation
```powershell
python ml/evaluation/deep_validation_analysis.py
```

### Step 7: Final Frozen Test Evaluation (Writers 46–55)
```powershell
python ml/evaluation/evaluate.py --checkpoint artifacts/models/champion_siamese_model.pt --calibrated-threshold artifacts/models/champion_threshold.json --test-pairs data/pairs/test_pairs.csv --output artifacts/evaluation/champion_test_evaluation_results.json --roc-plot docs/CHAMPION_ROC_CURVE.png --far-frr-plot docs/CHAMPION_FAR_FRR_CURVE.png --dist-plot docs/CHAMPION_SCORE_DISTRIBUTIONS.png --fa-cases artifacts/evaluation/champion_false_acceptance_cases.json --fr-cases artifacts/evaluation/champion_false_rejection_cases.json --batch-size 64
```

### Step 8: CLI Inference & Writer 46 Diagnostic Check
```powershell
python ml/experiments/check_writer_46.py
```

### Step 9: Automated Regression Test Suite
```powershell
python -m pytest -q
python tests/test_siamese_system.py
python tests/test_traceability.py
```

### Step 10: API & Web Dashboard Launch
```powershell
# Launch FastAPI Backend (Terminal 1)
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Dashboard UI is accessible at:
# http://localhost:8000/ (Direct FastAPI web interface mount)
# http://localhost:5173/ (Vite/Node frontend server)
```
