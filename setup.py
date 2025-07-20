#!/usr/bin/env python3
"""
TEBP Configuration Setup Script

This script sets up the TEBP project structure and generates config.yaml.
Usage:
    python create_config.py                    # Basic setup
"""

import os
import zipfile
import urllib.request
import platform
import subprocess

def get_current_path():
    """Get the current working directory as foundation_path"""
    return os.getcwd().replace("\\", "/")

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
    foundation_path = foundation_path.replace("\\", "/")
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
        "use_houdini": False,
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

def install_system_dependencies():
    """Install system-specific dependencies (torch, temurin)"""
    system = platform.system().lower()
    
    print(f"\n🔧 Installing system dependencies for {system}...")
    
    if system == "darwin":  # macOS
        print("Installing PyTorch for macOS...")
        try:
            # Install PyTorch nightly for macOS
            result = subprocess.run([
                "pip3", "install", "--pre", "torch", "torchvision", "torchaudio",
                "--extra-index-url", "https://download.pytorch.org/whl/nightly/cpu"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ PyTorch installed successfully for macOS")
                print(result.stdout)
            else:
                print("✗ Failed to install PyTorch for macOS")
                print(result.stderr)
                return False
            
            # Install Temurin (Java) for macOS
            print("Installing Temurin for macOS...")
            result = subprocess.run([
                "brew", "install", "--cask", "temurin"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ Temurin installed successfully for macOS")
                print(result.stdout)
                
                # Set JAVA_HOME
                java_home_result = subprocess.run([
                    "/usr/libexec/java_home"
                ], capture_output=True, text=True)
                
                if java_home_result.returncode == 0:
                    java_home = java_home_result.stdout.strip()
                    export_command = f'export JAVA_HOME={java_home}'
                    os.system(export_command)
                    print(f"✓ Set JAVA_HOME to: {java_home}")
                else:
                    print("⚠️  Could not set JAVA_HOME automatically")
            else:
                print("✗ Failed to install Temurin for macOS")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"✗ Error installing macOS dependencies: {e}")
            return False
            
    elif system == "linux":
        print("Installing PyTorch for Linux...")
        try:
            # Install PyTorch for Linux (CPU version)
            result = subprocess.run([
                "pip3", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cpu"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ PyTorch installed successfully for Linux")
                print(result.stdout)
            else:
                print("✗ Failed to install PyTorch for Linux")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"✗ Error installing Linux dependencies: {e}")
            return False
    
    else:
        print(f"⚠️  Unsupported system: {system}. Skipping system-specific dependencies.")
    
    return True

def install_requirements(foundation_path):
    """Install Python requirements from requirements.txt"""
    requirements_path = os.path.join(foundation_path, "requirements.txt")
    
    print("\n📦 Installing Python requirements...")
    
    if not os.path.exists(requirements_path):
        print(f"✗ requirements.txt not found at: {requirements_path}")
        return False
    
    try:
        print(f"Installing from: {requirements_path}")
        result = subprocess.run(["pip", "install", "-r", requirements_path], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Python requirements installed successfully!")
            print(result.stdout)
        else:
            print("✗ Failed to install Python requirements")
            print(result.stderr)
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error installing Python requirements: {e}")
        return False

def install_bullet3(foundation_path):
    """Install Bullet3 with PyBullet support"""
    import sys
    
    bullet_path = os.path.join(foundation_path, "00.third-party", "bullet3")
    build_path = os.path.join(bullet_path, "build")
    
    print("\n🔧 Installing Bullet3...")
    
    try:
        # Create build directory
        print("Creating build directory...")
        os.makedirs(build_path, exist_ok=True)
        print(f"✓ Created build directory: {build_path}")
        
        # Change to build directory
        os.chdir(build_path)
        print(f"✓ Changed to build directory: {build_path}")
        
        # Run cmake
        print("Running cmake...")
        result = subprocess.run(["cmake", "-DBUILD_PYBULLET=ON", ".."], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ CMake configuration successful")
            print(result.stdout)
        else:
            print("✗ CMake configuration failed")
            print(result.stderr)
            return False
        
        # Run make
        print("Running make...")
        if sys.platform == "darwin":  # macOS
            cpu_count = subprocess.run(["sysctl", "-n", "hw.logicalcpu"], 
                                       capture_output=True, text=True).stdout.strip()
        elif sys.platform.startswith("linux"):  # Linux
            cpu_count = subprocess.run(["nproc"], 
                                       capture_output=True, text=True).stdout.strip()
        result = subprocess.run(["make", "-j", cpu_count], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Make build successful")
            print(result.stdout)
        else:
            print("✗ Make build failed")
            print(result.stderr)
            return False
        
        # Install PyBullet
        pybullet_path = os.path.join(build_path, "examples", "pybullet")
        if os.path.exists(pybullet_path):
            os.chdir(pybullet_path)
            print(f"✓ Changed to pybullet directory: {pybullet_path}")
            
            # Get Python site-packages directory
            result = subprocess.run([sys.executable, "-m", "site", "--user-site"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                site_packages = result.stdout.strip()
                os.makedirs(site_packages, exist_ok=True)
                print(f"✓ Created site-packages directory: {site_packages}")
                
                # Copy pybullet.so
                pybullet_so = os.path.join(pybullet_path, "pybullet.so")
                if os.path.exists(pybullet_so):
                    import shutil
                    shutil.copy2(pybullet_so, site_packages)
                    print(f"✓ Copied pybullet.so to: {site_packages}")
                else:
                    print(f"✗ pybullet.so not found at: {pybullet_so}")
                    return False
            else:
                print("✗ Failed to get Python site-packages directory")
                return False
        else:
            print(f"✗ PyBullet directory not found: {pybullet_path}")
            return False
        
        print("✓ Bullet3 installation completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error during Bullet3 installation: {e}")
        return False

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
    
    # 3. Generate config.yaml
    print("\n⚙️  Generating config.yaml...")
    generate_config_yaml(foundation_path)
    
    # 4. Install system dependencies (torch, temurin)
    install_system_dependencies()
    
    # 5. Install Python requirements
    install_requirements(foundation_path)
    
    # 6. Install Bullet3
    install_bullet3(foundation_path)
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Manually download run-time.zip and dataset.zip from OneDrive")
    print("2. Unzip run-time.zip and dataset.zip to TEBP/data/run-time/ and TEBP/data/dataset/")
    print("3. Update config.yaml paths if needed")
    print("\nUsage examples:")
    print("  python create_config.py                    # Basic setup")

if __name__ == "__main__":
    main() 