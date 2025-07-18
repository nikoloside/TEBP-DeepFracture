import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from utils_config import load_config as root_load_config

def load_config(config_path="./config.yaml"):
    """
    Load config file and replace variables
    """
    return root_load_config(config_path)

def get_training_config():
    """
    Get training config
    """
    config = load_config()
    return config