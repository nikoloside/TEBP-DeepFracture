#!/usr/bin/env python3
"""
TEBP Configuration Setup Script

This script sets up the TEBP project structure and generates config.yaml.
Usage:
    python create_config.py                    # Basic setup
    python create_config.py with_runtime       # Setup with runtime download
    python create_config.py with_data          # Setup with dataset download
    python create_config.py with_runtime with_data  # Setup with both downloads
"""

import os
import sys
import yaml
import zipfile
import urllib.request
from pathlib import Path
import shutil

def get_current_path():
    """Get the current working directory as foundation_path"""
    return os.getcwd()

def create_folders(foundation_path):
    """Create required folders"""
    folders = [
        "data/dataset",
        "data/run-time"
    ]
    
    for folder in folders:
        full_path = os.path.join(foundation_path, folder)
        os.makedirs(full_path, exist_ok=True)
        print(f"✓ Created folder: {full_path}")

def download_and_extract(url, extract_path, filename=None):
    """Download and extract a zip file"""
    if filename is None:
        filename = url.split('/')[-1]
    
    zip_path = os.path.join(extract_path, filename)
    
    print(f"Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, zip_path)
        print(f"✓ Downloaded: {filename}")
        
        # Extract the zip file
        print(f"Extracting {filename}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print(f"✓ Extracted: {filename}")
        
        # Clean up the zip file
        os.remove(zip_path)
        print(f"✓ Cleaned up: {filename}")
        
    except Exception as e:
        print(f"✗ Error downloading/extracting {filename}: {e}")
        return False
    
    return True

def generate_config_yaml(foundation_path):
    """Generate the config.yaml file"""
    config = {
        "# 01 Data Generation": None,
        "shape_category": "_out_base",
        "foundation_path": foundation_path,
        "": None,
        "data_path": "${foundation_path}/data/src",
        "data_norm_path": "${foundation_path}/data/norm",
        "data_bullet_path": "${foundation_path}/data/bullet",
        "": None,
        "# 01.03 Simulation Machine Manager": None,
        "# Refer to /01.Data-generation/04-SimulationInstanceManager/config.yaml": None,
        "": None,
        "# 01.04 Dashboard": None,
        "# Refer to /01.Data-generation/05-Dashboard/.env.local": None,
        "# Refer to /01.Data-generation/05-Dashboard/data.json": None,
        "": None,
        "# 02 Cook Data": None,
        "data_gdrive_path": "${foundation_path}/data/gdrive",
        "data_inputSdf_path": "${foundation_path}/data/dataset/input/sdf",
        "data_input_path": "${foundation_path}/data/dataset/input",
        "data_output_path": "${foundation_path}/data/dataset/output",
        "data_dataset_path": "${foundation_path}/data/dataset/SharedResults",
        "": None,
        "# 03 Training": None,
        "max_impulse": 304527,
        "save_path": "${foundation_path}/data/dataset/run",
        "dataroot": "${foundation_path}/data/dataset/_out_base",
        "runName": "base-VQVAE-0/",
        "projName": "base",
        "log_wandb": False,
        "use_cuda": True,
        "train_dataset_size": 250,
        "train_cookbook_size": 250,
        "test_dataset_size": 50,
        "": None,
        "# 04 Run-time": None,
        "fiji_path": "${foundation_path}/data/run-time/fiji/Fiji.app",
        "data_runtime_workspace_path": "${foundation_path}/data/run-time/Runs/",
        "data_runtime_data_path": "${foundation_path}/data/run-time/Experiments/",
        "source_runtime_path": "${foundation_path}/04.Run-time",
        "use_houdini": True,
        "houdini_path": "/Applications/Houdini/Houdini20.5.584/Frameworks/Python.framework/Versions/3.11/bin/python3.11",
        "houdini_libs": "/Applications/Houdini/Houdini20.5.584/Frameworks/Houdini.framework/Versions/Current/Resources/houdini/python3.11libs/"
    }
    
    # Write config to file
    config_path = os.path.join(foundation_path, "config.yaml")
    
    with open(config_path, 'w') as f:
        for key, value in config.items():
            if key.startswith('#'):
                f.write(f"{key}\n")
            elif key == "":
                f.write("\n")
            else:
                if isinstance(value, bool):
                    f.write(f"{key}: {str(value)}\n")
                elif isinstance(value, int):
                    f.write(f"{key}: {value}\n")
                else:
                    f.write(f"{key}: \"{value}\"\n")
    
    print(f"✓ Generated config.yaml at: {config_path}")

def main():
    """Main function"""
    print("🚀 TEBP Configuration Setup")
    print("=" * 50)
    
    # 1. Check current path as foundation_path
    foundation_path = get_current_path()
    print(f"Foundation path: {foundation_path}")
    
    # 2. Create folders
    print("\n📁 Creating folders...")
    create_folders(foundation_path)
    
    # 3. Handle with_runtime argument
    if len(sys.argv) > 1 and "with_runtime" in sys.argv:
        print("\n📥 Downloading run-time files...")
        runtime_path = os.path.join(foundation_path, "data/run-time")
        
        runtime_url = "https://univtokyo-my.sharepoint.com/personal/7553042866_utac_u-tokyo_ac_jp/_layouts/15/download.aspx?UniqueId=532d8eb0%2Da9ab%2D4e88%2Dab06%2D5e40ae6dbbf9"
        if runtime_url != "link":
            download_and_extract(runtime_url, runtime_path, "run-time.zip")
        else:
            print("⚠️  Please replace 'link' with actual download URL for run-time.zip")
    else:
        print("\n⏭️  Skipping runtime download (use 'with_runtime' flag to download)")
    
    # 4. Handle with_data argument
    if len(sys.argv) > 1 and "with_data" in sys.argv:
        print("\n📥 Downloading dataset files...")
        dataset_path = os.path.join(foundation_path, "data/dataset")
        
        dataset_url = "https://univtokyo-my.sharepoint.com/personal/7553042866_utac_u-tokyo_ac_jp/_layouts/15/download.aspx?UniqueId=e317f88c%2D3c79%2D4ffc%2D94e7%2D24a623cd476a"
        if dataset_url != "link_2":
            download_and_extract(dataset_url, dataset_path)
        else:
            print("⚠️  Please replace 'link_2' with actual download URL for dataset")
    
    # 5. Generate config.yaml
    print("\n⚙️  Generating config.yaml...")
    generate_config_yaml(foundation_path)
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Replace 'link' and 'link_2' with actual download URLs")
    print("2. Update config.yaml paths if needed")
    print("3. Install required dependencies")
    print("\nUsage examples:")
    print("  python create_config.py                    # Basic setup")
    print("  python create_config.py with_runtime       # Setup with runtime download")
    print("  python create_config.py with_data          # Setup with dataset download")
    print("  python create_config.py with_runtime with_data  # Setup with both downloads")

if __name__ == "__main__":
    main()
