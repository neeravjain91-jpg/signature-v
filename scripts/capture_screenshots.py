"""
Captures real desktop screenshots of all 7 SIGNATURE VMAKE pages
using Microsoft Edge headless mode.
"""
import os
import sys
import time
import subprocess
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT_DIR = Path("docs/screenshots")
OUT_DIR.mkdir(parents=True, exist_ok=True)

PAGES = [
    ("01_case_review.png", "/"),
    ("02_manual_workflow.png", "/manual-workflow"),
    ("03_verification_studio.png", "/verification-studio"),
    ("04_model_comparison.png", "/model-comparison"),
    ("05_compliance_queue.png", "/compliance-queue"),
    ("06_audit_timeline.png", "/audit-timeline"),
    ("07_model_registry.png", "/model-registry")
]

def check_server():
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/v1/health", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False

def main():
    if not Path(EDGE_EXE).exists():
        print(f"Error: Edge binary not found at {EDGE_EXE}")
        sys.exit(1)

    server_proc = None
    if not check_server():
        print("Starting local FastAPI server...")
        server_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        for _ in range(30):
            time.sleep(0.5)
            if check_server():
                print("Server is ready.")
                break
        else:
            print("Failed to start server.")
            if server_proc:
                server_proc.kill()
            sys.exit(1)
    else:
        print("Server is already running.")

    try:
        for filename, route in PAGES:
            target_url = f"{BASE_URL}{route}"
            out_file = (OUT_DIR / filename).resolve()
            print(f"Capturing: {route} -> {filename}...")
            cmd = [
                EDGE_EXE,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--window-size=1440,900",
                f"--screenshot={str(out_file)}",
                target_url
            ]
            subprocess.run(cmd, check=True)
            if out_file.exists():
                size_kb = out_file.stat().st_size / 1024.0
                print(f"  [OK] Saved {out_file.name} ({size_kb:.1f} KB)")
            else:
                print(f"  [FAIL] Could not capture {filename}")
    finally:
        if server_proc:
            print("Terminating server...")
            server_proc.terminate()
            server_proc.wait()

    print("\nAll page screenshots captured successfully!")

if __name__ == "__main__":
    main()
