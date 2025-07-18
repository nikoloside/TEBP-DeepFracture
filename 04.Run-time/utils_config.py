import sys
import os
# Import the parent directory's utils_config directly
parent_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, parent_dir)
import utils_config as root_utils_config

def load_config(config_path="config.yaml"):
    """
    Load config file and replace variables
    """
    # Import here to avoid circular import issues
    import importlib.util
    spec = importlib.util.spec_from_file_location("root_utils_config", os.path.join(parent_dir, "utils_config.py"))
    root_utils_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(root_utils_config)
    return root_utils_config.load_config(config_path)

def get_training_config():
    """
    Get training config
    """
    config = load_config()
    return config 