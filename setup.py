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
import argparse
import sys

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

def download_from_huggingface(repo_id, local_dir, repo_type="model"):
    """Download files from Hugging Face"""
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("✗ huggingface_hub not installed. Please install it first:")
        print("  pip install huggingface_hub")
        return False
    
    print(f"Downloading from Hugging Face: {repo_id}")
    try:
        if repo_type == "dataset":
            # For datasets, download specific files
            snapshot_download(repo_id=repo_id, local_dir=local_dir, repo_type="dataset")
        else:
            # For models, download all files
            snapshot_download(repo_id=repo_id, local_dir=local_dir)
        print(f"✓ Downloaded from {repo_id} to {local_dir}")
        return True
    except Exception as e:
        print(f"✗ Error downloading from {repo_id}: {e}")
        return False

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
    
    # Determine Fiji path based on operating system
    if platform.system().lower() == "linux":
        fiji_path = "${foundation_path}/data/run-time/fiji/fiji-linux64/Fiji.app"
    else:
        fiji_path = "${foundation_path}/data/run-time/fiji/Fiji.app"
    
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
        "fiji_path": fiji_path,
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
            
            # Try to install Temurin (Java) for macOS using Homebrew
            print("Installing Temurin for macOS (Homebrew)...")
            result = subprocess.run([
                "brew", "install", "--cask", "temurin"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ Temurin installed successfully for macOS via Homebrew")
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
                # Try MacPorts as fallback
                print("Trying MacPorts for Temurin installation...")
                result = subprocess.run([
                    "sudo", "port", "install", "openjdk24-temurin"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✓ Temurin installed successfully for macOS via MacPorts")
                    java_home = "/opt/local/libexec/openjdk24.0.1"
                    export_command = f'export JAVA_HOME={java_home}'
                    os.system(export_command)
                    print(f"✓ Set JAVA_HOME to: {java_home}")
                else:
                    print("✗ Failed to install Temurin via both Homebrew and MacPorts")
                    print("Please install Java manually and set JAVA_HOME")
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

def build_bullet3(foundation_path):
    """Build Bullet3 with PyBullet support"""
    import sys
    
    bullet_path = os.path.join(foundation_path, "00.third-party", "bullet3")
    build_path = os.path.join(bullet_path, "build")
    
    print("\n🔧 Building Bullet3...")
    
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
        result = subprocess.run(["cmake", "-DBUILD_PYBULLET=ON", "..", "-DCMAKE_POLICY_VERSION_MINIMUM=3.5"], 
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
        else:
            print("⚠️  Unsupported system for Bullet3 build. Skipping...")
            return False
        
        result = subprocess.run(["make", "-j", cpu_count], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Make build successful")
            print(result.stdout)
        else:
            print("✗ Make build failed")
            print(result.stderr)
            return False
                
    except Exception as e:
        print(f"✗ Error during Bullet3 build: {e}")
        return False
    
def copy_bullet3(foundation_path):
    """Copy Bullet3 with PyBullet support"""
    import sys
    
    bullet_path = os.path.join(foundation_path, "00.third-party", "bullet3")
    build_path = os.path.join(bullet_path, "build")
    
    print("\n🔧 Copying Bullet3...")
    
    try:
        # Install PyBullet
        pybullet_path = os.path.join(build_path, "examples", "pybullet")
        if os.path.exists(pybullet_path):
            os.chdir(pybullet_path)
            print(f"✓ Changed to pybullet directory: {pybullet_path}")
            
            # Get Python site-packages directory
            import sysconfig
            venv_plat = sysconfig.get_path('platlib')

            result = venv_plat
            
            site_packages = result
            os.makedirs(site_packages, exist_ok=True)
            print(f"✓ Created site-packages directory: {site_packages}")
            
            # Copy pybullet.so or pybullet.pyd
            pybullet_bin = os.path.join(pybullet_path, "pybullet.so")
            if os.path.exists(pybullet_bin):
                import shutil
                shutil.copy2(pybullet_bin, site_packages)
                print(f"✓ Copied pybullet.so to: {site_packages}")
            else:
                pybullet_bin = os.path.join(build_path, "lib", "Release", "pybullet.pyd")
                if os.path.exists(pybullet_bin):
                    import shutil
                    shutil.copy2(pybullet_bin, site_packages)
                    print(f"✓ Copied pybullet.pyd to: {site_packages}")
                else:
                    print("✗ Failed to find pybullet.so or pybullet.pyd")
                    return False
        else:
            print(f"✗ PyBullet directory not found: {pybullet_path}")
            return False
        
        print("✓ Bullet3 copy completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error during Bullet3 copy: {e}")
        return False

def download_huggingface_models(foundation_path):
    """Download DeepFracture model, CSV files, and OBJ files from Hugging Face"""
    print("\n🤗 Downloading DeepFracture files from Hugging Face...")
    
    # Create data directories
    data_dir = os.path.join(foundation_path, "data")
    run_time_dir = os.path.join(data_dir, "run-time")
    
    os.makedirs(run_time_dir, exist_ok=True)
    
    # Download DeepFracture model
    print("Downloading DeepFracture model...")
    model_success = download_from_huggingface(
        repo_id="nikoloside/deepfracture",
        local_dir=run_time_dir,
        repo_type="model"
    )
    
    if model_success:
        print("✓ DeepFracture files downloaded successfully!")
        print("Files available in data/run-time/")
        print("Structure:")
        print("  - Models: base/, bunny/, lion/, pot/, squirrel/")
        print("  - CSV files: csv/")
        print("  - OBJ files: objs/")
        return True
    else:
        print("⚠️  Download failed. Please check the errors above.")
        return False

def install_bullet3(foundation_path):
    """Install Bullet3 with PyBullet support"""
    build_bullet3(foundation_path)
    copy_bullet3(foundation_path)

def create_virtual_environment(foundation_path, venv_name="venv"):
    """Create a virtual environment if it doesn't exist"""
    venv_path = os.path.join(foundation_path, venv_name)
    
    if os.path.exists(venv_path):
        print(f"✓ Virtual environment already exists at: {venv_path}")
        return True
    
    print(f"\n🐍 Creating virtual environment at: {venv_path}")
    try:
        result = subprocess.run([sys.executable, "-m", "venv", venv_path], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Virtual environment created successfully!")
            print(f"To activate: source {venv_path}/bin/activate")
            return True
        else:
            print("✗ Failed to create virtual environment")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Error creating virtual environment: {e}")
        return False

def setup_java_home():
    """Set up JAVA_HOME environment variable"""
    print("\n☕ Setting up JAVA_HOME...")
    
    system = platform.system().lower()
    java_home = None
    
    # Check Java version first
    try:
        java_version_result = subprocess.run(["java", "-version"], 
                                           capture_output=True, text=True)
        if java_version_result.returncode == 0:
            print("✓ Java is installed and accessible")
            print(f"Java version output: {java_version_result.stderr.strip()}")
        else:
            print("⚠️  Java command failed")
    except Exception as e:
        print(f"⚠️  Could not run java -version: {e}")
    
    # System-specific Java detection
    if system == "windows":
        print("Detected Windows system")
        try:
            # Use 'where java' to find Java executable
            where_result = subprocess.run(["where", "java"], 
                                        capture_output=True, text=True, shell=True)
            if where_result.returncode == 0:
                java_path = where_result.stdout.strip().split('\n')[0]
                print(f"Found Java at: {java_path}")
                # Extract JAVA_HOME from java path
                if "bin\\java.exe" in java_path:
                    java_home = java_path.replace("\\bin\\java.exe", "")
                    print(f"Extracted JAVA_HOME: {java_home}")
        except Exception as e:
            print(f"Error finding Java on Windows: {e}")
    
    elif system == "darwin":
        print("Detected macOS system")
        try:
            # Use /usr/libexec/java_home -V to list all Java installations
            java_home_result = subprocess.run(["/usr/libexec/java_home", "-V"], 
                                            capture_output=True, text=True)
            if java_home_result.returncode == 0:
                print("Available Java installations:")
                print(java_home_result.stderr)  # -V outputs to stderr
                
                # Get the default Java home
                default_result = subprocess.run(["/usr/libexec/java_home"], 
                                              capture_output=True, text=True)
                if default_result.returncode == 0:
                    java_home = default_result.stdout.strip()
                    print(f"Default JAVA_HOME: {java_home}")
        except Exception as e:
            print(f"Error finding Java on macOS: {e}")
    
    elif system == "linux":
        print("Detected Linux system")
        try:
            # Use readlink -f to get real Java path and extract JAVA_HOME
            cmd = "readlink -f \"$(which java)\""
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                real_java_path = result.stdout.strip()
                print(f"Real Java path: {real_java_path}")
                
                # Extract JAVA_HOME (remove /bin/java)
                if "/bin/java" in real_java_path:
                    java_home = real_java_path.replace("/bin/java", "")
                    print(f"✓ JAVA_HOME: {java_home}")
                else:
                    print("✗ Could not extract JAVA_HOME")
                    java_home = None
            else:
                print("✗ Failed to get Java path")
                java_home = None
        except Exception as e:
            print(f"Error finding Java on Linux: {e}")
            java_home = None
    
    # Fallback: Check common Java locations if system-specific detection failed
    if not java_home:
        print("System-specific detection failed, trying common locations...")
        possible_paths = [
            "/usr/lib/jvm/java-21-openjdk-amd64",  # Ubuntu
            "/usr/lib/jvm/java-17-openjdk-amd64",  # Ubuntu
            "/usr/lib/jvm/java-11-openjdk-amd64",  # Ubuntu
            "/opt/local/libexec/openjdk24.0.1",    # MacPorts
            "/Library/Java/JavaVirtualMachines/temurin-24.jdk/Contents/Home",  # macOS Homebrew
            "/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home",  # macOS Homebrew
            "/Library/Java/JavaVirtualMachines/temurin-11.jdk/Contents/Home",  # macOS Homebrew
            "C:\\Program Files\\Java\\jdk-21",  # Windows
            "C:\\Program Files\\Java\\jdk-17",  # Windows
            "C:\\Program Files\\Java\\jdk-11",  # Windows
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                java_home = path
                print(f"Found Java in common location: {java_home}")
                break
    
    if java_home:
        print(f"✓ Found Java at: {java_home}")
        
        # Add to shell profile
        shell_profile = None
        home_dir = os.path.expanduser("~")
        
        # Determine shell profile file based on system
        if system == "windows":
            # Windows: Set environment variable
            try:
                import winreg
                # Set JAVA_HOME in Windows registry
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Environment")
                winreg.SetValueEx(key, "JAVA_HOME", 0, winreg.REG_EXPAND_SZ, java_home)
                winreg.CloseKey(key)
                print(f"✓ Set JAVA_HOME in Windows registry: {java_home}")
                
                # Note: JAVA_HOME will be available after restart or running: refreshenv
                print(f"✓ JAVA_HOME set in registry: {java_home}")
                print("  Please restart your terminal or run: refreshenv")
                return True
            except Exception as e:
                print(f"⚠️  Could not set JAVA_HOME in Windows registry: {e}")
                print(f"  Please manually set: setx JAVA_HOME \"{java_home}\"")
                return False
        else:
            # Unix-like systems: Use shell profile
            if os.path.exists(os.path.join(home_dir, ".zshrc")):
                shell_profile = os.path.join(home_dir, ".zshrc")
            elif os.path.exists(os.path.join(home_dir, ".bashrc")):
                shell_profile = os.path.join(home_dir, ".bashrc")
            elif os.path.exists(os.path.join(home_dir, ".bash_profile")):
                shell_profile = os.path.join(home_dir, ".bash_profile")
            elif os.path.exists(os.path.join(home_dir, ".profile")):
                shell_profile = os.path.join(home_dir, ".profile")
            else:
                shell_profile = None
        
        if shell_profile:
            # Check if JAVA_HOME is already set
            try:
                with open(shell_profile, 'r') as f:
                    content = f.read()
                    if f'JAVA_HOME={java_home}' in content or f'JAVA_HOME="{java_home}"' in content:
                        print(f"✓ JAVA_HOME already configured in {shell_profile}")
                        print(f"  Please run: source {shell_profile} to activate in current session")
                        return True
            except:
                pass
            
            # Add JAVA_HOME to shell profile
            export_line = f'\n# JAVA_HOME for TEBP\nexport JAVA_HOME="{java_home}"\n'
            try:
                with open(shell_profile, 'a') as f:
                    f.write(export_line)
                print(f"✓ Added JAVA_HOME to {shell_profile}")
                print(f"  Please run: source {shell_profile} to activate in current session")
                return True
            except Exception as e:
                print(f"⚠️  Could not write to {shell_profile}: {e}")
                print(f"  Please manually add: export JAVA_HOME='{java_home}'")
                return False
        else:
            print("⚠️  Could not find shell profile file")
            print(f"  Please manually add: export JAVA_HOME='{java_home}'")
            return False
    else:
        print("✗ Could not find Java installation")
        print("  Please install Java and set JAVA_HOME manually")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="TEBP Configuration Setup")
    parser.add_argument("--skip-downloads", action="store_true", 
                       help="Skip downloading models and datasets from Hugging Face")
    parser.add_argument("--skip-system-deps", action="store_true",
                       help="Skip installing system dependencies (PyTorch, Java)")
    parser.add_argument("--skip-bullet3", action="store_true",
                       help="Skip building Bullet3")
    parser.add_argument("--create-venv", action="store_true",
                       help="Create a virtual environment")
    parser.add_argument("--venv-name", type=str, default="venv",
                       help="Name for virtual environment (default: venv)")
    
    args = parser.parse_args()
    
    print("🚀 TEBP Configuration Setup")
    print("=" * 50)
    
    # 1. Check current path as foundation_path
    foundation_path = get_current_path()
    print(f"Foundation path: {foundation_path}")
    
    # 2. Create virtual environment (optional)
    if args.create_venv:
        create_virtual_environment(foundation_path, args.venv_name)
    
    # 3. Create folders
    print("\n📁 Creating folders...")
    create_folders(foundation_path)
    
    # 3. Generate config.yaml
    print("\n⚙️  Generating config.yaml...")
    generate_config_yaml(foundation_path)
    
    # 4. Set up JAVA_HOME
    setup_java_home()
    
    # 5. Install system dependencies (torch, temurin)
    if not args.skip_system_deps:
        install_system_dependencies()
    else:
        print("\n⏭️  Skipping system dependencies installation")
    
    # 6. Install Python requirements
    install_requirements(foundation_path)
    
    # 7. Install Bullet3
    if not args.skip_bullet3:
        install_bullet3(foundation_path)
    else:
        print("\n⏭️  Skipping Bullet3 installation")
    
    # 8. Download DeepFracture model from Hugging Face
    if not args.skip_downloads:
        download_huggingface_models(foundation_path)
    else:
        print("\n⏭️  Skipping Hugging Face downloads")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    if not args.skip_downloads:
        print("✓ DeepFracture files downloaded from Hugging Face")
        print("  Files available in data/run-time/")
        print("  Structure: models/, csv/, objs/")
    else:
        print("1. Download DeepFracture files manually from Hugging Face:")
        print("   - Repository: https://huggingface.co/nikoloside/deepfracture")
        print("   - Extract to data/run-time/")
        print("   - Contains: models/, csv/, objs/ folders")
    print("2. Update config.yaml paths if needed")
    print("3. Run: python 04.Run-time/predict-runtime.py")
    print("\nUsage examples:")
    print("  python setup.py                           # Full setup")
    print("  python setup.py --create-venv             # Create virtual environment")
    print("  python setup.py --create-venv --venv-name tebp-env  # Custom venv name")
    print("  python setup.py --skip-downloads          # Skip Hugging Face downloads")
    print("  python setup.py --skip-system-deps        # Skip system dependencies")
    print("  python setup.py --skip-bullet3            # Skip Bullet3 build")

if __name__ == "__main__":
    main() 