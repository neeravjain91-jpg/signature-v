"""
Automated Dataset Download and Setup Script.

Downloads and extracts the CEDAR offline signature dataset.
Respects academic licenses and allows local file extraction or manual placement.
"""

import os
import sys
import shutil
import zipfile
import argparse
import urllib.request
from pathlib import Path
import yaml


def load_config(config_path: str = "ml/data/dataset_config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_dataset_present(raw_dir: Path, cfg: dict) -> bool:
    genuine_dir = raw_dir / cfg["structure"]["genuine_dir_name"]
    forged_dir = raw_dir / cfg["structure"]["forged_dir_name"]
    if genuine_dir.exists() and forged_dir.exists():
        num_gen = len(list(genuine_dir.glob("*.png")))
        num_forg = len(list(forged_dir.glob("*.png")))
        if num_gen > 0 and num_forg > 0:
            return True
    return False


def download_file_with_progress(url: str, dest_path: Path):
    print(f"[*] Downloading from: {url}")
    print(f"[*] Destination: {dest_path}")
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    
    with urllib.request.urlopen(req) as response:
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        
        with open(dest_path, "wb") as out_file:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    pct = (downloaded / total_size) * 100
                    mb_down = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    sys.stdout.write(f"\r    -> {mb_down:.1f} MB / {mb_total:.1f} MB ({pct:.1f}%)")
                    sys.stdout.flush()
                else:
                    mb_down = downloaded / (1024 * 1024)
                    sys.stdout.write(f"\r    -> {mb_down:.1f} MB downloaded")
                    sys.stdout.flush()
        print("\n[+] Download completed successfully.")


def extract_archive(archive_path: Path, target_dir: Path, cfg: dict):
    print(f"[*] Extracting archive: {archive_path} -> {target_dir}")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    temp_extract = target_dir / "_temp_extract"
    temp_extract.mkdir(parents=True, exist_ok=True)
    
    try:
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(temp_extract)
        
        # Locate full_org and full_forg inside the extracted tree
        found_gen = None
        found_forg = None
        for root, dirs, files in os.walk(temp_extract):
            if cfg["structure"]["genuine_dir_name"] in dirs:
                found_gen = Path(root) / cfg["structure"]["genuine_dir_name"]
            if cfg["structure"]["forged_dir_name"] in dirs:
                found_forg = Path(root) / cfg["structure"]["forged_dir_name"]
        
        if not found_gen or not found_forg:
            # Check if root itself directly contains images
            raise RuntimeError("Could not find full_org and full_forg in the extracted archive.")
        
        dest_gen = target_dir / cfg["structure"]["genuine_dir_name"]
        dest_forg = target_dir / cfg["structure"]["forged_dir_name"]
        
        if dest_gen.exists():
            shutil.rmtree(dest_gen)
        if dest_forg.exists():
            shutil.rmtree(dest_forg)
            
        shutil.move(str(found_gen), str(dest_gen))
        shutil.move(str(found_forg), str(dest_forg))
        
        print(f"[+] Placed genuine signatures in: {dest_gen}")
        print(f"[+] Placed forged signatures in: {dest_forg}")
    finally:
        if temp_extract.exists():
            shutil.rmtree(temp_extract, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Download and setup the CEDAR signature verification dataset.")
    parser.add_argument("--config", default="ml/data/dataset_config.yaml", help="Path to config YAML")
    parser.add_argument("--force", action="store_true", help="Force redownload even if present")
    parser.add_argument("--archive", type=str, default=None, help="Path to existing local zip archive")
    args = parser.parse_args()

    cfg = load_config(args.config)
    raw_dir = Path(cfg["paths"]["raw_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)

    if not args.force and is_dataset_present(raw_dir, cfg):
        gen_dir = raw_dir / cfg["structure"]["genuine_dir_name"]
        forg_dir = raw_dir / cfg["structure"]["forged_dir_name"]
        num_gen = len(list(gen_dir.glob("*.png")))
        num_forg = len(list(forg_dir.glob("*.png")))
        print(f"[+] Dataset is already present at {raw_dir}:")
        print(f"    - Genuine signatures ({cfg['structure']['genuine_dir_name']}): {num_gen} files")
        print(f"    - Forged signatures ({cfg['structure']['forged_dir_name']}): {num_forg} files")
        print("Use --force to redownload and reinstall if necessary.")
        return

    if args.archive:
        archive_path = Path(args.archive)
        if not archive_path.is_file():
            print(f"[-] Provided archive {archive_path} does not exist.")
            sys.exit(1)
        extract_archive(archive_path, raw_dir, cfg)
    else:
        download_url = cfg["dataset"]["sources"]["official_zip_mirror"]
        download_zip = raw_dir / "cedar_dataset.zip"
        download_file_with_progress(download_url, download_zip)
        extract_archive(download_zip, raw_dir, cfg)
        if download_zip.exists():
            os.remove(download_zip)

    # Final summary check
    gen_dir = raw_dir / cfg["structure"]["genuine_dir_name"]
    forg_dir = raw_dir / cfg["structure"]["forged_dir_name"]
    num_gen = len(list(gen_dir.glob("*.png")))
    num_forg = len(list(forg_dir.glob("*.png")))
    print(f"\n[+] Setup Complete!")
    print(f"    Genuine samples: {num_gen}")
    print(f"    Forged samples:  {num_forg}")
    print(f"    Total samples:   {num_gen + num_forg}")


if __name__ == "__main__":
    main()
